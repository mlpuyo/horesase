#! py -3
# -*- coding: utf-8 -*-
import os
import sys
import pickle
import webbrowser
import mecab_func
# nltkはロードが遅い
from nltk.metrics.distance import masi_distance

'''
コマンドライン引数から読み込んだ文章で類似度検索
mecabのpythonバインディングのインストールは次から(mac, linux)
※気が向く限りPEP8に則る
'''


def main():

    # pickleがなければ実行。時間がかかる
    # make_pickle_from_json()
    if not(os.path.exists('meigenWords.bin')):
        mecab_func.update_misawa_json()

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
    matched_inf = {}
    for meigen in meigenWords:
        words = meigen['words']

        # Jaccard距離による類似度判定。小さいほど類似
        # r = nltk.metrics.distance.jaccard_distance(set(tweetWords), set(words))

        # MASI距離による類似度判定。小さいほど類似
        r = masi_distance(set(tweetWords), set(words))

        if r < min_r:
            min_r = r
            matched_inf = meigen

    print("r = %f" % min_r)
    print(matched_inf)
    print("tweetWords: %s" % tweetWords)
    webbrowser.open(matched_inf['image'])

if __name__ == '__main__':
    main()
