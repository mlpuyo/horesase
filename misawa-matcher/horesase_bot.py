#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import pickle
import urllib
import shutil
import tweepy
import datetime
import yaml  # pip install pyyaml
import mecab_func
import matcher_main
import key
import logging.config
from logging import getLogger
"""
matcher_main.pyを利用してTwitterAPIを叩く
"""

# デバッグ用に特定アカウントのみを対象として実行
DEBUG = False
# ユーザ探索時の投稿日時の下限
SDATE = datetime.datetime.utcnow() - datetime.timedelta(days=1)
# 送りつけたtweetidのキャッシュファイル名
ID_DUMP_FN = "stidDic.bin"


# -------------------------------------
# logger生成
# -------------------------------------
def setup_logging(
    default_path='logging.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """ Setup logging configuration
    http://goo.gl/7BbSIs
    """
    if not os.path.exists("log"):
        os.mkdir("log")
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            logging.config.dictConfig(yaml.load(f.read()))
    else:
        logging.basicConfig(level=default_level)

setup_logging('logging.yaml')
logger = getLogger(__name__)
# -------------------------------------


def api_authenticate():
    """ API認証
    """
    try:
        auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET)
        auth.set_access_token(key.OAUTH_TOKEN, key.OAUTH_SECRET)
    except:
        logger.critical("API Connection Error", exc_info=True)
        sys.exit()
    return tweepy.API(auth)


def api_search_user_with_name(api, user_dic):
    """ ユーザ検索
    - IN  : api認証 api_authenticate(), ユーザの辞書
    """
    at_name = '@' + key.BOT_NAME
    stid_dic = {}
    try:
        candidate_tweets = api.search(q=at_name)
    except:
        logger.error('api-seach error', exc_info=True)

    if (os.path.exists(ID_DUMP_FN)):
        with open(ID_DUMP_FN, 'rb') as f:
            try:
                stid_dic = pickle.load(f)
            except:
                logger.error('empty pickle file', exc_info=True)

    for tweet in candidate_tweets:
        # SDATE以前のツイートは無視する
        if tweet.created_at < SDATE:
            continue

        if not(tweet.id in stid_dic):
            stid_dic[tweet.id] = {"screen_name": tweet.user.screen_name,
                                  "created_at": tweet.created_at}
        else:
            continue

        if not(tweet.user.screen_name in user_dic):
            user_dic[tweet.user.screen_name] = "message user"

    # 自分は削る
    if key.BOT_NAME in user_dic:
        del user_dic[key.BOT_NAME]

    with open(ID_DUMP_FN, 'wb') as f:
        pickle.dump(stid_dic, f)


def api_get_followers(api, user_dic):
    """ 全フォロワーとフォローを取得
    - IN  : api認証 api_authenticate(), ユーザの辞書
    """
    try:
        c = tweepy.Cursor(api.friends, id=key.BOT_NAME)
        for friend in c.items():
            user_dic[friend.screen_name] = "follower"

        c = tweepy.Cursor(api.followers, id=key.BOT_NAME)
        for friend in c.items():
            user_dic[friend.screen_name] = "friend"
    except:
        logger.critical("failed to get followers/friends", exc_info=True)

    return user_dic


def get_user_text(api, user, meigenWords, tr=0.98):
    """ 任意ユーザの直近ツイート10件を取得
    ツイートとミサワ画像のurlを返却
    ※10件というのはとりあえずの値
    - IN  : api認証, ユーザ, 名言辞書
    - OUT : ユーザのツイート, ミサワのurl, 成功可否のbool値
    """
    try:
        user_tweets = api.user_timeline(id=user, count=20)
    except:
        logging.critical("user_timeline fetch error", exc_info=True)

    minr = 999.
    target_index = 0
    matched_url = ""

    stid_dic = {}
    if (os.path.exists(ID_DUMP_FN)):
        with open(ID_DUMP_FN, 'rb') as f:
            try:
                stid_dic = pickle.load(f)
            except EOFError:
                logger.error('empty pickle file', exc_info=True)

    for i, tweet in enumerate(user_tweets):
        _id = tweet.id
        if not DEBUG:
            # 二重投稿防止
            if _id in stid_dic:
                continue
            # SDATE以前のツイートは無視する
            if tweet.created_at < SDATE:
                continue
            # 他ユーザへのリプライは対象外
            if "@" in tweet.text and not ("@" + key.BOT_NAME in tweet.text):
                continue
        try:
            r, url = matcher_main.search_misawa_with_masi(meigenWords, tweet.text, retMasiR=True)
        except UnicodeEncodeError:
            logging.warning("UnicodeEncodeError", exc_info=True)
            continue
        except:
            logging.error("Unexpected Error", exc_info=True)
            continue

        if r < minr:
            target_index = i
            minr = r
            matched_url = url

    if minr < tr:
        if not DEBUG:
            stid_dic[user_tweets[target_index].id] = {
                "screen_name": user_tweets[target_index].user.screen_name,
                "created_at": user_tweets[target_index].created_at}

            with open(ID_DUMP_FN, 'wb') as f:
                pickle.dump(stid_dic, f)

        return user_tweets[target_index], matched_url, True
    else:
        logging.info("no meigen matched: minr=[%f]" % minr)
        return "no_tweet", "no_image", False


def main():
    # 色々準備
    if not(os.path.exists('meigenWords.bin')):
        mecab_func.update_json()

    with open('meigenWords.bin', 'rb') as f:
        try:
            meigenWords = pickle.load(f)
        except EOFError:
            logger.error('empty pickle file', exc_info=True)

    # Twitter利用
    api = api_authenticate()
    if DEBUG:
        user_dic = {'horesase_test1':'follower'}
    else:
        logger.info("========searching user========")
        user_dic = {}
        api_get_followers(api, user_dic)
        api_search_user_with_name(api, user_dic)
        logger.info("==============================\n")

    logger.info("========calculating masi for users========")
    for user, cls in user_dic.items():
        logger.info("user:[%s], class:[%s]" % (user, cls))
        if cls == "follower" or "friend":
            user_tweet, pic_url, isMatched = get_user_text(api, user, meigenWords, 0.955)
        else:
            user_tweet, pic_url, isMatched = get_user_text(api, user, meigenWords, 0.98)

        if not isMatched:
            continue

        # 画像をダウンロード
        try:
            with urllib.request.urlopen(pic_url) as response, open('picture.gif', 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except:
            logger.error('misawa download error', exc_info=True)
            continue
        # ユーザの投稿内容に画像をつけて投稿
        reply_text = '@' + user + ' ' + user_tweet.text
        logger.info("reply_text:[%s]" % reply_text)
        logger.info("url:[%s]" % pic_url)
        try:
            api.update_with_media('picture.gif', reply_text, in_reply_to_status_id=user_tweet.id)
        except:
            logger.error('reply error', exc_info=True)
    logger.info("==========================================")


if __name__ == '__main__':
    logger.info("[START]")
    main()
    logger.info("[END]\n\n")
