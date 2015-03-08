#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, pickle, urllib, shutil, datetime
import tweepy, MeCab
import mecab_func, matcher_main
import key

'''
matcher_main.pyを利用してTwitterAPIを叩く
'''

def api_authenticate():
    ''' API認証
    '''
    auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET)
    auth.set_access_token(key.OAUTH_TOKEN, key.OAUTH_SECRET)

    return tweepy.API(auth)


def api_search_user(api):
    '''　ユーザ検索
    '''
    at_name = '@' + key.BOT_NAME
    candidate_tweets = api.search(q=at_name)
    user_list = []
    stid_list = []

    if (os.path.exists('stidList.bin')):
        with open('stidList.bin', 'rb') as f:
            try:
                stid_list = pickle.load(f)
            except EOFError:
                print('empty pickle file....')

    for tweet in candidate_tweets:
        '''本当はここで重複削除とかもしたい
        '''
        if not(tweet.id in stid_list):
            stid_list.append(tweet.id)
        else:
            continue 

        if not(tweet.user.screen_name in user_list):
            user_list.append(tweet.user.screen_name)
            print(tweet.user.screen_name)

    '''自分は削る
    '''
    if key.BOT_NAME in user_list:
        del user_list[user_list.index(key.BOT_NAME)]

    with open('stidList.bin', 'wb') as f:
        pickle.dump(stid_list, f)

    return user_list


def get_user_text(api, user, meigenWords):
    '''　
    任意ユーザの直近ツイート10件を取得し、
    その中からベストマッチの名言を導出して返却する.
    ※10件というのはとりあえずの値
    '''
    user_tweets = api.user_timeline(id=user, count=10)
    minr = 999
    target_index = 0
 
    stid_list = []
    if (os.path.exists('stidList.bin')):
        with open('stidList.bin', 'rb') as f:
            try:
                stid_list = pickle.load(f)
            except EOFError:
                print('empty pickle file....')

    for i, tweet in enumerate(user_tweets):
        _id = tweet.id
        if _id in stid_list:
            continue
        r, inf = matcher_main.search_misawa_with_masi2(meigenWords, tweet.text)
        if r < minr:
            target_index = i
            minr = r
 
    stid_list.append(user_tweets[target_index].id)
    with open('stidList.bin', 'wb') as f:
        pickle.dump(stid_list, f)
            
    return user_tweets[target_index]

def main():
    '''
    '''
    # 色々準備
    if not(os.path.exists('meigenWords.bin')):
        mecab_func.update_misawa_json()

    with open('meigenWords.bin', 'rb') as f:
        try:
            meigenWords = pickle.load(f)
        except EOFError:
            print('empty pickle file...')
    
    #　Twitter利用
    api = api_authenticate()
    user_list = api_search_user_with_name(api)
    
    for user in user_list:
        user_tweet = get_user_text(api,user,meigenWords)

        # 名言のURLを取得	
        pic_url = matcher_main.search_misawa_with_masi(meigenWords, user_tweet.text)
        
        '''もっとスマートに画像を貼っつける方法があったら知りたい
        '''
        with urllib.request.urlopen(pic_url) as response, open('picture.gif', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        '''とりあえず画像に付け足すテキストは元のものをそのまま使う
        '''
        reply_text = '@' + user + ' ' + user_tweet.text
        api.update_with_media('picture.gif',reply_text,in_reply_status_id='513704088840568834')
#        api.update_status(reply_text, in_reply_status_id=user_tweet.id)
        print(user_tweet.id)


if __name__ == '__main__':
    main()
