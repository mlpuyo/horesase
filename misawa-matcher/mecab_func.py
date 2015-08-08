#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import pickle
import csv
import unicodedata
import MeCab
import shutil
import urllib.request
from gensim import corpora, models, similarities
from logging import getLogger
logger = getLogger(__name__)


def breakdown_into_validwords(sentence):
    """
    与えられた文章(文字列)を形態素解析してリスト返却します
    - 入出力例
    -   IN:  "今日はいい天気ですね"
    -   OUT: ['今日', '天気']
    """
    ret_list = []

    if sentence == '' or not(isinstance(sentence, str)):
        return ret_list

    sentence = sentence.replace("\n", "")

    model = MeCab.Model_create("-Ochasen -d mecab-ipadic-neologd")
    tagger = model.createTagger()
    lines = tagger.parse(sentence).split('\n')
    for line in lines:
        if line == "EOS":
            break
        line = line.split('\t')
        word = line[2]

        # 卑猥な単語を含む文章は除外
        if word in ['ちんちん', 'ちんこ', 'キンタマ', 'きんたま', '痴漢']:
            return []
        # TODO:除外リストの作成
        if word in ['今日', '俺', '私', '僕', '人', '思う', 'ちゃう',
                '何', '行く', 'もらう', 'られる', 'くれる', 'すぎる']:
            continue
        try:
            jtype = unicodedata.name(word[0])
        except:
            continue
        # 漢字でない一文字のwordは無視
        # 'ー'や'*'も同様
        if len(word) == 1 and jtype[0:4] != 'CJK ':
            continue
        # 二文字のひらがなは無視
        if (len(word) == 2 and jtype[0:4] == 'HIRA'
                and unicodedata.name(word[1])[0:4] == 'HIRA'):
            continue
        # 伸ばし棒を含むひらがなは無視
        if jtype[0:4] == 'HIRA' and 'ー' in word:
            continue
        if jtype[0:4] == 'LATI':
            continue
        if word.isdigit():
            continue
        if (line[3][:2] == '名詞' or line[3][:2] == '動詞'
                or line[3][:2] == '副詞' or line[3][:3] == '形容詞'):
            ret_list.append(word)
            # print(word)

    return ret_list


def make_pickle_from_json(fn='meigens.json'):
    """"
    名言辞書の形態素解析
    - 辞書型の配列を作成
    - pickle保存
    """
    logger.info("making pickels...")
    with open(fn, 'r', encoding='utf-8') as f:
        meigenRowData = json.load(f)

    dictionary = corpora.Dictionary.load_from_text('model/jawiki_wordids.txt.bz2')
    lsi100 = models.LsiModel.load("model/lsi100.model")
    lsi300 = models.LsiModel.load("model/lsi300.model")
    lda100 = models.LdaModel.load("model/lda100.model")
    lda200 = models.LdaModel.load("model/lda200.model")
    lda300 = models.LdaModel.load("model/lda300.model")

    meigenData = []
    for meigen in meigenRowData:

        if not os.path.exists("img"):
            os.mkdir("img")
        imgName = 'img/' + str(meigen['id']) + '.gif'


        if not os.path.exists(imgName):
            try:
                with urllib.request.urlopen(meigen['image'], timeout=100) as response, open(imgName, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except:
                logger.error('Could not download img id=[%s]' % meigen['id'], exc_info=True)

        # if meigen['character'] in ['ちんちんでか男(30)', 'チーポー(2)']:
        #     continue
        data = {}
        words = breakdown_into_validwords(meigen['body'])
        # title_words = breakdown_into_validwords(meigen['title'])

        # タイトルに含まれる単語が本文にも含まれる場合は削除
        # for word in words:
        #     if word in title_words:
        #         title_words.remove(word)

        # words += title_words
        if len(words) <= 1:
            continue

        data['id'] = meigen['id']
        data['image'] = meigen['image']
        data['character'] = meigen['character']
        data['title'] = meigen['title']
        data['body'] = meigen['body']
        data['words'] = words
        data['lsi100'] = lsi100[dictionary.doc2bow(words)]
        data['lsi300'] = lsi300[dictionary.doc2bow(words)]
        data['lda100'] = lda100[dictionary.doc2bow(words)]
        data['lda200'] = lda200[dictionary.doc2bow(words)]
        data['lda300'] = lda300[dictionary.doc2bow(words)]

        meigenData.append(data)
        if data['id'] % 50 == 0:
            logger.info('id = %d' % data['id'])

    with open('data/meigenWords.bin', 'wb') as f:
        pickle.dump(meigenData, f)

    with open('data/meigenWords.csv', mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        for data in meigenData:
            writer.writerow(data["words"])

    logger.info("pickels updated. meigen count:[%s]" % len(meigenData))


def update_json(url='http://horesase.github.io/horesase-boys/meigens.json'):
    """
    名言辞書を最新化します
    - 名言辞書をURLもしくはローカルから取得
    - 名言辞書の形態素解析
    """

    # 名言辞書の更新
    try:
        logger.info("downloading json...")
        r = urllib.request.urlopen(url)
    except:
        logger.error('Could not download json\nCheck Internet Connetcion...', exc_info=True)
        return
    with open("data/meigens.json", "wb") as f:
        f.write(r.read())

    logger.info("file[meigens.json] updated")

    # デシリアライズと形態素解析
    make_pickle_from_json('data/meigens.json')


def test_func_1(sentence):
    logger.info("input: [%s]" % sentence)
    logger.info("output:[%s]" % breakdown_into_validwords(sentence))


def test_func_2():
    update_json()


if __name__ == '__main__':
    """
    単独実行時の処理
    - テストしたい処理を記述する
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    # test_func_1('今日はいい天気ですね')
    test_func_2()
