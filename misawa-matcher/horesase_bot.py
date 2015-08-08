#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import pickle
import urllib
import shutil
import tweepy
import datetime
import yaml  # pip install pyyaml
import mecab_func
import matcher_main
from data import key
from gensim import corpora, models, similarities, matutils
import logging.config
from logging import getLogger
"""
matcher_main.pyを利用してTwitterAPIを叩く
"""

# デバッグ用に特定アカウントのみを対象として実行
DEBUG = False
# ユーザ探索時の投稿日時の下限
SDATE = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
# 送りつけたtweetidのキャッシュファイル名
ID_DUMP_FN = "data/stidDic.bin"


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
    tweet_to_reply = []
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
                    "text": tweet.text,
                    "created_at": tweet.created_at}
        else:
            continue

        if not(tweet.user.screen_name in user_dic):
            user_dic[tweet.user.screen_name] = "message user"

        tweet_to_reply.append(tweet)

    # 自分は削る
    if key.BOT_NAME in user_dic:
        del user_dic[key.BOT_NAME]

    with open(ID_DUMP_FN, 'wb') as f:
        pickle.dump(stid_dic, f)

    return tweet_to_reply


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


def get_user_text(api, user, meigenWords, tr=0.98,
        method='masi', model=None, dictionary=None):
    """ 任意ユーザの直近ツイート10件を取得
    ツイートとミサワ画像の辞書を返却
    ※10件というのはとりあえずの値
    - IN  : api認証, ユーザ, 名言辞書
    - OUT : ユーザのツイート, ミサワの辞書, 成功可否のbool値
    """
    try:
        user_tweets = api.user_timeline(id=user, count=20)
    except:
        logging.critical("user_timeline fetch error", exc_info=True)
        return "no_tweet", "no_image", False

    minr = 999.
    target_index = 0
    matched_meigen = {}

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
            r, meigen = matcher_main.search_misawa(meigenWords, tweet.text,
                         retR=True, method=method, model=model, dictionary=dictionary)
        except UnicodeEncodeError:
            logging.warning("UnicodeEncodeError", exc_info=True)
            continue
        except:
            logging.error("Unexpected Error", exc_info=True)
            continue

        if r < minr:
            target_index = i
            minr = r
            matched_meigen = meigen

    if minr < tr:
        if not DEBUG:
            stid_dic[user_tweets[target_index].id] = {
                "screen_name": user_tweets[target_index].user.screen_name,
                "text": user_tweets[target_index].text,
                "created_at": user_tweets[target_index].created_at}

            with open(ID_DUMP_FN, 'wb') as f:
                pickle.dump(stid_dic, f)

        return user_tweets[target_index], matched_meigen, True
    else:
        logging.info("no meigen matched: minr=[%f]" % minr)
        return "no_tweet", "no_image", False


def make_reply_text(user,  tweet):
    '''ユーザ名とつぶやきの内容から、返信内容を整形
    - IN  : ユーザ名,  statusオブジェクト
    - OUT : 返信内容の文字列
    '''
    # 本来ptnは使いまわしたほうが好ましい
    ptn1 = re.compile('https?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+')  # urlを除外
    ptn2 = re.compile('[#＃][Ａ-Ｚａ-ｚA-Za-z一-鿆0-9０-９ぁ-ヶｦ-ﾟー]+')  # ハッシュタグを除外
    ptn3 = re.compile('【.+】|[0-9]+RT\s?')  # 拡散希望等のタグ、スパムのRT等
    ptn4 = re.compile('[wｗWW]{4,}|\n+')  # 4回以上のｗ、改行はスペース一つに
    ptn5 = re.compile('(、|。|!|！|\?|？|\.|．|…|w|ｗ|」|】|』)\s')  # 文末の空白

    text = tweet.text
    text = re.sub(ptn1, '', text)
    text = re.sub(ptn2, '', text)
    text = re.sub(ptn3, '', text)
    text = re.sub(ptn4, ' ', text)
    text = re.sub(ptn5, r'\1', text)  # 文末の空白は除外
    text = re.sub(r'\s+', ' ', text)  # 2つ以上の空白は1つに
    text = re.sub(r'\s+$', '', text)  # 末尾の空白は削除

    text = text.replace('「', '『')
    text = text.replace('」', '』')
    text = "「" + text + "」"

    reply_text = "@" + user + "\n"
    reply_text += re.sub(r'\n|\s', '', tweet.author.name)
    reply_text += text
    return reply_text


def reply_to_status(api, meigen, user, user_tweet):
    '''対象のツイートに対しリプライを返す
    - IN  : 返信する名言の辞書, ユーザオブジェクト, ツイートオブジェクト
    '''
    # 画像のパス
    pathToImg = 'img/' + str(meigen['id']) + '.gif'
    if not os.path.exists(pathToImg):
        logger.error('misawa download error', exc_info=True)            
        return

    # ユーザの投稿内容に画像をつけて投稿
    reply_text = make_reply_text(user, user_tweet)
    logger.info("reply_text:[%s]" % reply_text)
    logger.info("url:[%s]" % meigen['image'])
    try:
        # api.update_with_media('data/picture.gif', reply_text, in_reply_to_status_id=user_tweet.id)
        pass
    except:
        logger.error('reply error', exc_info=True)
    return


def main():
    # 色々準備
    if not(os.path.exists('data/meigenWords.bin')):
        mecab_func.update_json()

    with open('data/meigenWords.bin', 'rb') as f:
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
        tweet_to_reply = api_search_user_with_name(api, user_dic)

    logger.info("========calc start========")
    isModeled = False
    if len(sys.argv) >= 3:
        method = sys.argv[1]
        pathToModel = sys.argv[2]
        isModeled = True
    if len(sys.argv) >= 4:
        pathToDict = sys.argv[3]
    if isModeled:
        try:
            if method[0:3] in ["lda", "LDA"]:
                model = models.LdaModel.load(pathToModel)
                dictionary = corpora.Dictionary.load_from_text(pathToDict)
            elif method[0:3] in ["lsi", "LSI"]:
                model = models.LsiModel.load(pathToModel)
                dictionary = corpora.Dictionary.load_from_text(pathToDict)
            elif method[0:3] in ["d2v", "doc"]:
                d2v   = models.doc2vec.Doc2Vec(hashfxn=matcher_main.myhashfxn)
                d2v   = d2v.load(pathToModel)
                model = models.LsiModel.load(pathToModel)
            else:
                logger.critical("invalid model")
                sys.exit()
            logger.info("model loaded")
        except:
            logger.critical("failed to load model", exc_info=True)
            sys.exit()

    for user, cls in user_dic.items():
        logger.info("user:[%s], class:[%s]" % (user, cls))
        if isModeled:
            if cls == "follower" or "friend":
                user_tweet, meigen, isMatched = get_user_text(api, user, meigenWords,
                        tr=-0.7, method=method, model=model, dictionary=dictionary)
            else:
                user_tweet, meigen, isMatched = get_user_text(api, user, meigenWords,
                        tr=-0.1, method=method, model=model, dictionary=dictionary)
        else:
            if cls == "follower" or "friend":
                user_tweet, meigen, isMatched = get_user_text(api, user, meigenWords, 0.955)
            else:
                user_tweet, meigen, isMatched = get_user_text(api, user, meigenWords, 0.98)

        if not isMatched:
            continue

        reply_to_status(api, meigen, user, user_tweet) 

    for tweet in tweet_to_reply:
        if isModeled:
            r, meigen = matcher_main.search_misawa(meigenWords, tweet.text,
                         retR=True, method=method, model=model, dictionary=dictionary)
        else:
            r, meigen = matcher_main.search_misawa(meigenWords, tweet.text, retR=True)
        # TODO:微妙な場合用に汎用性のある画像をリプライする
        if isModeled:
            tr = -0.1
        else:
            tr = 0.98
        if r < tr:
            try:
                reply_to_status(meigen, tweet.user.screen_name, tweet)
            except:
                logging.error("Unexpected Error", exc_info=True)

    logger.info("==========================================")


if __name__ == '__main__':
    logger.info("[START]")
    main()
    logger.info("[END]\n\n")
