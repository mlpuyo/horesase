#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import pickle
import webbrowser
import mecab_func
# nltkはロードが遅い
from nltk.metrics.distance import masi_distance

"""
コマンドライン引数から読み込んだ文章で類似度検索
※気が向く限りPEP8に則る
"""

def search_misawa_with_masi(meigens, targetSentence, retMasiR=False):
    """
    MASI距離によりベストなミサワを探す関数
    - IN  : 名言リスト、解析対象文章
    - OUT : 画像のURL
    """
    targetWords = mecab_func.breakdown_into_validwords(targetSentence)
    
    if len(targetWords) == 0:
        print("解析ができないよ. 文章を入れてね")
        return(1)

    # 入力された文章で解析可能な場合
    hit = False
    minr = 1.0
    matched_inf = {}
    cnt = 0

    for meigen in meigens:

        words = meigen['words']

        # Jaccard距離による類似度判定。小さいほど類似
        # r = nltk.metrics.distance.jaccard_distance(set(tweetWords), set(words))

        # MASI距離による類似度判定。小さいほど類似
        r = masi_distance(set(targetWords), set(words))
        # print("%s dist:%s [%s] [%s]" % (cnt, r, targetSentence, meigen))
        # print("%s dist:[%s] [%s] [%s]" % (cnt, r, targetWords, words))

        if r < minr:
            hit = True
            minr = r
            matched_inf = meigen

        cnt = cnt + 1

    # 例外: すべての名言との距離が 1.0  
    if not hit:
        print("ベストマッチなし\n")
        if retMasiR:
            return 1., "no_image"
        else:
            return (1.)
    
    # レポート
    print("")
    print("meigens count: %s" % len(meigens))
    print("input: [%s]" % targetSentence)
    print("input_breakdown: %s" % targetWords)

    # 抽出された名言
    print("")
    print("selected meigen [r = %f]:" % minr)
    for k, v in matched_inf.items():
        if k == 'body':
            v = v.replace('\n', ' ')
        print('\t%s: %s' % (k, v))
    print("")

    if retMasiR:
        # 戻り値: MASI距離, 全ミサワ情報
        return minr, matched_inf['image']
    else:
        # 戻り値: 画像のURL
        return(matched_inf['image'])


def main():
    # pickleがなければ実行。時間がかかる
    # make_pickle_from_json()
    if not(os.path.exists('meigenWords.bin')):
        mecab_func.update_misawa_json()

    with open('meigenWords.bin', 'rb') as f:
        try:
            meigens = pickle.load(f)
        except EOFError:
            print('empty picke file...')

    # 引数を受け取らない場合、対話的に実行
    if len(sys.argv) < 2:
        print("\npress 'q' to quit...")
        sentence = ''
        while True:
            sentence = input("input sentence> ")
            if sentence == 'q':
                break
            elif sentence == '':
                continue
            search_misawa_with_masi(meigens, sentence)
    else:
        # ウェブブラウザで画像を表示
        # TODO: ウェブブラウザへの表示は、botとの兼ね合いも含めて検討
        # webbrowser.open(search_misawa_with_masi(meigenWords, sys.argv[1]))
        search_misawa_with_masi(meigens, sys.argv[1])


if __name__ == '__main__':
    main()
