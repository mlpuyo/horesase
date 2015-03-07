#!/usr/bin/env python
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


def search_misawa_with_masi(meigenWords, targetSentence):
    '''tweetからMASI距離によりベストなミサワを探す関数
    '''
    targetWords = mecab_func.breakdown_into_validwords(targetSentence)
    #targetWords = mecab_func.breakdown_into_validwords("ありがとう、郵便局。良い天気です")
    #targetWords = mecab_func.breakdown_into_validwords2(targetSentence)
    min_r = 100.
    matched_inf = {}
    for meigen in meigenWords:
        words = meigen['words']

        # Jaccard距離による類似度判定。小さいほど類似
        # r = nltk.metrics.distance.jaccard_distance(set(tweetWords), set(words))

        # MASI距離による類似度判定。小さいほど類似
        r = masi_distance(set(targetWords), set(words))

        if r < min_r:
            min_r = r
            matched_inf = meigen

	# 結果表示
    print("")
    print("meigens count: %s" % len(meigenWords))
    print("input: \"%s\"" % targetSentence)
    if len(targetWords) == 0:
        print("no breakdown with MeCab")
        return
    print("input_breakdown: %s" % targetWords)

    # 解析結果
    print("")
    print("selected meigen [r = %f]:" % min_r)
    for k, v in matched_inf.items():
        if k == 'body':
            v = v.replace('\n', ' ')
        print('\t%s: %s' % (k, v))
    print("")

    return(matched_inf['image'])


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
    if len(sys.argv) < 2:
        print("")
        print("press 'q' to quit...")
        sentence = ''
        while True:
            sentence = input("input sentence> ")
            if sentence == 'q':
                break
            elif sentence == '':
                continue
            search_misawa_with_masi(meigenWords, sentence)
    else:
    	# ウェブブラウザで画像を表示
        # webbrowser.open(search_misawa_with_masi(meigenWords, sys.argv[1]))
        search_misawa_with_masi(meigenWords, sys.argv[1])


if __name__ == '__main__':
    main()
