#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
from api_keys import *

# Tweepy
# http://docs.tweepy.org/en/v3.3.0/api.html

# API認証
# 注意: 各自api_keysクラスを用意すること
k = api_keys()	

auth = tweepy.OAuthHandler(k.CONSUMER_KEY, k.CONSUMER_SECRET)
auth.secure = True
auth.set_access_token(k.ACCESS_TOKEN, k.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)
print("authorized:[%s]" % api.me().name)
print("")

#
# tweets の取得
#    任意のユーザのツイート直近10件を取得します
#
statuses = api.user_timeline('tgck', count=10)

for status in statuses:
    print("============================================================")
    print("status_text:[%s]" % status.text)
    print("status_created_at:[%s]" % status.created_at)

print("")

