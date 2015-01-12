#! py -3
# -*- coding: utf-8 -*-
import json
import csv
import os
import sys
import nltk
import pickle
import webbrowser
import mecab_func

'''
コマンドライン引数から読み込んだ文章で類似度検索
mecabのpythonバインディングのインストールは次から(mac, linux)
pip install mecab-python3
'''



def main():

    # pickleがなければ実行。時間がかかる
    # make_pickle_from_json()
    if not(os.path.exists('meigenWords.bin')):
        make_pickle_from_json()

    with open('meigenWords.bin', 'rb') as f:
        try:
            meigenWords = pickle.load(f)
        except EOFError:
            print('empty picke file...')

    if len(sys.argv) <= 1:
        tweet = '今日はいい天気ですね'
        print(len(sys.argv))
    else:
        tweet = sys.argv[1]

    tweetWords = mecab_func.breakdown_into_validwords(tweet)

    min_r = 100.
    for meigen in meigenWords:
        words = meigen['words']

        # Jaccard距離による類似度判定。小さいほど類似
        # r = nltk.metrics.distance.jaccard_distance(set(tweetWords), set(words))

        # MASI距離による類似度判定。小さいほど類似
        r = nltk.metrics.distance.masi_distance(set(tweetWords), set(words))

        if r < min_r:
            min_r = r
            match_url = meigen['url']
            match_chr = meigen['chr']
            match_title = meigen['title']
            match_meigen = meigen['meigen']
            match_words = meigen['words']

    print("r = %f" % min_r)
    print("title: %s" % match_title)
    print("chr: %s" % match_chr)
    print("meigen: %s" % match_meigen.replace("\n", ""))
    print("words: %s" % match_words)
    print("tweetWords: %s" % tweetWords)
    webbrowser.open(match_url)

if __name__ == '__main__':
    main()
