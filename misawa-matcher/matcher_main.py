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


def search_misawa_with_masi(meigenWords, tweet):
    '''tweetからMASI距離によりベストなミサワを探す関数
    '''
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
    print("tweetWords: %s" % tweetWords)
    for k, v in matched_inf.items():
        if k == 'body':
            v = v.replace('\n', ' ')
        print('%s: %s' % (k, v))
    return(matched_inf['image'])


def search_misawa_with_masi2(meigenWords, tweet):
    '''突貫工事でもろもろreturnするよう変更
    '''
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
    # print("tweetWords: %s" % tweetWords)
    # for k, v in matched_inf.items():
    # if k == 'body':
    # v = v.replace('\n', ' ')
    # print('%s: %s' % (k, v))
    return(min_r, matched_inf)


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

    # 引数を受け取らない場合、対話的に実行
    if len(sys.argv) == 1:
        print("press 'q' to quit...")
        tweet = ''
        while True:
            tweet = input("input tweet> ")
            if tweet == 'q':
                break
            elif tweet == '':
                continue
            search_misawa_with_masi(meigenWords, tweet)
            print('\n')
    else:
        webbrowser.open(search_misawa_with_masi(meigenWords, sys.argv[1]))

if __name__ == '__main__':
    main()
