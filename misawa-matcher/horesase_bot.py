#! py -3
# -*- coding: utf-8 -*-
<<<<<<< HEAD
import os, sys, pickle, urllib, shutil, datetime
=======
import os, sys, pickle, urllib, shutil
>>>>>>> 7e0504f666745c745959d30ba852a42625ab6a14
import tweepy, MeCab
import mecab_func, matcher_main
import key

def authenticate():
<<<<<<< HEAD
    auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUER_SECRET)
=======
    # f = open("consumer_and_token", "r")
    # CK = f.readline().replace("\n", "")
    # CS = f.readline().replace("\n", "")
    # AT = f.readline().replace("\n", "")
    # AS = f.readline().replace("\n", "")

# t = Twitter( auth=OAuth(key.OAUTH_TOKEN, key.OAUTH_SECRET,
#                key.CONSUMER_KEY, key.CONSUMER_SECRET) )
    # auth = tweepy.OAuthHandler(CK, CS)
    # auth.set_access_token(AT, AS)

    # ちょっと書き換え
    auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET)
>>>>>>> 7e0504f666745c745959d30ba852a42625ab6a14
    auth.set_access_token(key.OAUTH_TOKEN, key.OAUTH_SECRET)

    return tweepy.API(auth)


<<<<<<< HEAD
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

=======
def search_user(api):
    candidate_tweets = api.search(q="@ml_horesase")
    user_list = []
    for tweet in candidate_tweets:
        # 本当はここで重複削除とかもしたい
>>>>>>> 7e0504f666745c745959d30ba852a42625ab6a14
        if not(tweet.user.screen_name in user_list):
            user_list.append(tweet.user.screen_name)
            print(tweet.user.screen_name)

<<<<<<< HEAD
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
=======
    # 自分は削る
    if "ml_horesase" in user_list:
        del user_list[user_list.index("ml_horesase")]
    return user_list


def get_user_text(api,user, meigenWords):
    user_tweets = api.user_timeline(id=user)
    minr = 999.
    target_index = 0
    dict = {}

    for i, tweet in enumerate(user_tweets):
        _id = tweet.id
        if _id in dict:  # 投稿済みのidは除外
>>>>>>> 7e0504f666745c745959d30ba852a42625ab6a14
            continue
        r, inf = matcher_main.search_misawa_with_masi2(meigenWords, tweet.text)
        if r < minr:
            target_index = i
<<<<<<< HEAD
            minr = r
 
    stid_list.append(user_tweets[target_index].id)
    with open('stidList.bin', 'wb') as f:
        pickle.dump(stid_list, f)
            
    return user_tweets[target_index]

=======

    # 本当はここでちゃんとした仕組みでテキストを選定したい
    return user_tweets[target_index]


>>>>>>> 7e0504f666745c745959d30ba852a42625ab6a14
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
<<<<<<< HEAD
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
=======
        user_tweet = get_user_text(api,user, meigenWords)
        pic_url = matcher_main.search_misawa_with_masi(meigenWords, user_tweet.text)
        
        # もっとスマートに画像を貼っつける方法があったら知りたい
        with urllib.request.urlopen(pic_url) as response, open('picture.gif', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        # とりあえず画像に付け足すテキストは元のものをそのまま使う
        reply_text = '@' + user + ' ' + user_tweet.text
        api.update_with_media('picture.gif',reply_text,in_reply_status_id=user_tweet.id)
>>>>>>> 7e0504f666745c745959d30ba852a42625ab6a14
#        api.update_status(reply_text, in_reply_status_id=user_tweet.id)
        print(user_tweet.id)


if __name__ == '__main__':
    main()
