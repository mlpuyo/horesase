#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import pickle
import webbrowser
import mecab_func
# nltkはロードが遅い
from nltk.metrics.distance import masi_distance
from gensim import corpora, models, similarities, matutils
from logging import getLogger
logger = getLogger(__name__)

"""
コマンドライン引数から読み込んだ文章で類似度検索
※気が向く限りPEP8に則る
"""

def search_misawa(meigens, targetSentence, retR=False,
        method='masi', model=None, dictionary=None):
    """
    MASI距離によりベストなミサワを探す関数
    - IN  : 名言リスト、解析対象文章
    - OUT : 画像のURL
    """
    targetWords = mecab_func.breakdown_into_validwords(targetSentence)
    
    if len(targetWords) <= 1:
        logger.warning("less than one word")
        if retR:
            return 1., "no_image"
        else:
            return (1.)

    # 入力された文章で解析可能な場合
    hit = False
    minr = 1.0
    matched_inf = {}
    cnt = 0

    for meigen in meigens:

        words = meigen['words']

        if method == 'jaccard':
            # Jaccard距離による類似度判定。小さいほど類似
            r = nltk.metrics.distance.jaccard_distance(set(targetWords), set(words))
        elif method == 'masi':
            # MASI距離による類似度判定。小さいほど類似
            r = masi_distance(set(targetWords), set(words))
        elif method[0:3] in ['lsi', 'lda']:
            # コサイン類似度で判定。負で評価し、小さいほど類似
            vec = model[dictionary.doc2bow(targetWords)]
            r = -1.*matutils.cossim(meigen[method], vec)

        if r < minr:
            hit = True
            minr = r
            matched_inf = meigen
        cnt = cnt + 1

    # 例外: すべての名言との距離が 1.0  
    if not hit:
        logger.info("ベストマッチなし")
        if retR:
            return 1., "no_image"
        else:
            return (1.)
    
    logger.info("========calculation report========")
    logger.info("method: %s [r = %f]" % (method, minr))
    logger.info("input : %s %s" % (targetSentence, targetWords))
    logger.info('meigen: %s %s' % (matched_inf['body'].replace('\n', ' '), matched_inf['words']))
    logger.info("==================================")

    if retR:
        # 戻り値: MASI距離, 全ミサワ情報
        return minr, matched_inf['image']
    else:
        # レポート
        # 戻り値: 画像のURL
        return(matched_inf['image'])


def compare_models(meigens):
    import urllib
    import shutil
    with open("data/tweet.txt", "r", encoding="utf-8") as f:
        tweets = []
        for line in f:
            tweets.append(line[:-1])

    dictionary = corpora.Dictionary.load_from_text('model/jawiki_wordids.txt.bz2')
    lsi100 = models.LsiModel.load("model/lsi100.model")
    lsi300 = models.LsiModel.load("model/lsi300.model")
    lda100 = models.LdaModel.load("model/lda100.model")
    lda200 = models.LdaModel.load("model/lda200.model")
    lda300 = models.LdaModel.load("model/lda300.model")

    if not os.path.exists('out'):
        os.mkdir('out')
    for i, tweet in enumerate(tweets):
        dir = 'out/' + str(i + 1)
        if not os.path.exists(dir):
            os.mkdir(dir)
        for method, model in [['lsi100', lsi100], ['lsi300', lsi300],
                              ['lda100', lda100], ['lda200', lda200],
                              ['lda300', lda300], ['masi', None]]:
            r, url = search_misawa(meigens, tweet, retR=True,
                    method=method, model=model, dictionary=dictionary)
            if r >= 1:
                continue
            try:
                with urllib.request.urlopen(url) as response, open(
                        dir + '/' + method + str(int(-r*100)) + '.gif', 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except:
                pass


def main():
    # pickleがなければ実行。時間がかかる
    if not(os.path.exists('data/meigenWords.bin')):
        mecab_func.update_json()
        logger.info("data/meigenWords updated")

    try:
        with open('data/meigenWords.bin', 'rb') as f:
            meigens = pickle.load(f)
    except FileNotFoundError:
        logger.error('meigenWords not found', exc_info=True)
    except:
        logger.error('empty pickle file', exc_info=True)

    compare_models(meigens)

    # 引数を受け取らない場合、対話的に実行
    # if len(sys.argv) < 2:
    #     print("\npress 'q' to quit...")
    #     sentence = ''
    #     while True:
    #         sentence = input("input sentence> ")
    #         if sentence == 'q':
    #             break
    #         elif sentence == '':
    #             continue
    #         search_misawa_with_masi(meigens, sentence)
    # else:
    #     search_misawa_with_masi(meigens, sys.argv[1])


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    main()
