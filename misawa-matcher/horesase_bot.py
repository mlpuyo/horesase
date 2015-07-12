#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import pickle
import urllib
import shutil
import tweepy
import datetime
import mecab_func
import matcher_main
import key

"""
matcher_main.pyを利用してTwitterAPIを叩く
"""

# デバッグ用に特定アカウントのみを対象として実行
DEBUG = False
# ユーザ探索時の投稿日時の下限
SDATE = datetime.datetime.utcnow() - datetime.timedelta(days=3)
ID_DUMP_FN = "stidDic.bin"


def api_authenticate():
    """ API認証
    """
    try:
        auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET)
        auth.set_access_token(key.OAUTH_TOKEN, key.OAUTH_SECRET)
    except:
        print("API Connection Error")
        sys.exit()

    return tweepy.API(auth)


def api_search_user_with_name(api, user_dic):
    """ ユーザ検索
    - IN  : api認証 api_authenticate(), ユーザの辞書
    """
    at_name = '@' + key.BOT_NAME
    candidate_tweets = api.search(q=at_name)
    stid_dic = {}

    if (os.path.exists(ID_DUMP_FN)):
        with open(ID_DUMP_FN, 'rb') as f:
            try:
                stid_dic = pickle.load(f)
            except EOFError:
                print('empty pickle file....')

    for tweet in candidate_tweets:
        # SDATE以前のツイートは無視する
        if tweet.created_at < SDATE:
            continue

        if not(tweet.id in stid_dic):
            stid_dic[tweet.id] = {"screen_name":tweet.user.screen_name,
                    "created_at":tweet.created_at}
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
        c = tweepy.Cursor(api.friends , id=key.BOT_NAME)
        for friend in c.items():
            user_dic[friend.screen_name] = "follower"

        c = tweepy.Cursor(api.followers , id=key.BOT_NAME)
        for friend in c.items():
            user_dic[friend.screen_name] = "friend"
    except:
        print("API Connection Error")
        sys.exit()

    print(user_dic)
    return user_dic


def get_user_text(api, user, meigenWords, tr=0.98):
    """ 任意ユーザの直近ツイート10件を取得
    ツイートとミサワ画像のurlを返却
    ※10件というのはとりあえずの値
    - IN  : api認証, ユーザ, 名言辞書
    - OUT : ユーザのツイート, ミサワのurl, 成功可否のbool値
    """
    user_tweets = api.user_timeline(id=user, count=10)
    minr = 999.
    target_index = 0

    stid_dic = {}
    if (os.path.exists(ID_DUMP_FN)):
        with open(ID_DUMP_FN, 'rb') as f:
            try:
                stid_dic = pickle.load(f)
            except EOFError:
                print('empty pickle file....')

    for i, tweet in enumerate(user_tweets):
        _id = tweet.id
        if not DEBUG:
            if _id in stid_dic:
                continue            
        try:
            r, url = matcher_main.search_misawa_with_masi(meigenWords, tweet.text, retMasiR=True)
        except UnicodeEncodeError:
            print("UnicodeEncodeError")
            continue
        except:
            print("Unexpected Error")
            continue

        if r < minr:
            target_index = i
            minr = r

    if minr < tr:
        if not DEBUG:
            stid_dic[user_tweets[target_index].id] = {
                    "screen_name":user_tweets[target_index].user.screen_name,
                    "created_at":user_tweets[target_index].created_at}

            with open(ID_DUMP_FN, 'wb') as f:
                pickle.dump(stid_dic, f)

        return user_tweets[target_index], url, True
    else:
        print("no matched meigen:r=[%f]" % minr)
        print("")
        return "no_tweet", "no_image", False


def main():
    # 色々準備
    if not(os.path.exists('meigenWords.bin')):
        mecab_func.update_misawa_json()

    with open('meigenWords.bin', 'rb') as f:
        try:
            meigenWords = pickle.load(f)
        except EOFError:
            print('empty pickle file...')

    # Twitter利用
    api = api_authenticate()
    if DEBUG:
        user_dic = {'horesase_test1'}
    else:
        user_dic = {}
        api_get_followers(api, user_dic)
        api_search_user_with_name(api, user_dic)

    for user, cls in user_dic.items():
        print("user:[%s]" % user)
        print("class:[%s]" % cls)
        if cls == "follower" or "friend":
            user_tweet, pic_url, isMatched = get_user_text(api, user, meigenWords, 0.70)
        else:
            user_tweet, pic_url, isMatched = get_user_text(api, user, meigenWords, 0.95)

        if isMatched == False:
            continue

        # 画像をダウンロード
        with urllib.request.urlopen(pic_url) as response, open('picture.gif', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        # ユーザの投稿内容に画像をつけて投稿
        reply_text = '@' + user + ' ' + user_tweet.text
        print(reply_text)
        print(pic_url)
        print("")
        # api.update_with_media('picture.gif', reply_text, in_reply_status_id='user_tweet.id')


if __name__ == '__main__':
    main()
