#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
from api_keys import *

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
# mention の取得
#    自身に宛てられたmentionを1件取得します
#
mentions = api.mentions_timeline(count=1)

for mention in mentions:
    print("metion:[%s]" % mention.text)
    print("user:['%s]" % mention.user.screen_name)

print("")


