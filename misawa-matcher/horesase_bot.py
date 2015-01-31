#! py -3
# -*- coding: utf-8 -*-
import os, sys, pickle, urllib, shutil, datetime
import tweepy, MeCab
import mecab_func, matcher_main
import key

def authenticate():
    auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUER_SECRET)
    auth.set_access_token(key.OAUTH_TOKEN, key.OAUTH_SECRET)

    return tweepy.API(auth)


def search_user(api):    
    candidate_tweets = api.search(q="@ml_horesase")
    user_list = []
    stid_list = []

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
    if "ml_horesase" in user_list:
        del user_list[user_list.index("ml_horesase")]

    with open('stidList.bin', 'wb') as f:
        pickle.dump(stid_list, f)

    return user_list


def get_user_text(api, user, meigenWords):
    user_tweets = api.user_timeline(id=user)
    minr = 999
    target_index = 0
 
    stid_list = []
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
    '''色々準備
    '''
    if not(os.path.exists('meigenWords.bin')):
        mecab_func.update_misawa_json()

    with open('meigenWords.bin', 'rb') as f:
        try:
            meigenWords = pickle.load(f)
        except EOFError:
            print('empty pickle file...')

    api = authenticate()
    user_list = search_user(api)
    
    for user in user_list:
        user_tweet = get_user_text(api,user,meigenWords)
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
