#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import pickle
import csv
import unicodedata
import MeCab
import urllib.request
from subprocess import Popen, PIPE
from datetime import datetime


def breakdown_into_validwords(sentence):
    """
    与えられた文章(文字列)を形態素解析してリスト返却します
    - 入出力例
    -   IN:  "今日はいい天気ですね"
    -   OUT: ['今日', '天気']
    """
    ret_list = []

    if sentence == '' or not(isinstance(sentence, str)):
        """
        TODO: 例外処理
        """
        return ret_list

    sentence = sentence.replace("\n", "")

    model = MeCab.Model_create("-Ochasen")
    tagger = model.createTagger()
    lines = tagger.parse(sentence).split('\n')
    for line in lines:
        if line == "EOS":
            break
        line = line.split('\t')
        word = line[2]

        # 漢字でない一文字のwordは無視
        # 'ー'や'*'も同様
        if len(word) == 1 and unicodedata.name(word[0])[0:4] != 'CJK ':
            continue
        # 二文字のひらがなは無視
        if (len(word) == 2 and unicodedata.name(word[0])[0:4] == 'HIRA'
                and unicodedata.name(word[1])[0:4] == 'HIRA'):
            continue
        if (line[3][:2] == '名詞' or line[3][:2] == '動詞'
                or line[3][:2] == '副詞' or line[3][:3] == '形容詞'):
            ret_list.append(word)
            # print(word)

    return ret_list


def make_pickle_from_json(fn='../meigens.json'):
    """"
    名言辞書の形態素解析
    - 辞書型の配列を作成
    - pickle保存
    """
    print("making pickels...")
    with open(fn, 'r', encoding='utf-8') as f:
        meigenRowData = json.load(f)

    meigenData = []
    for meigen in meigenRowData:
        data = {}
        words = breakdown_into_validwords(meigen['body'])
        title_words = breakdown_into_validwords(meigen['title'])
        words += title_words
        if len(words) <= 1:
            continue

        data['id'] = meigen['id']
        data['image'] = meigen['image']
        data['character'] = meigen['character']
        data['title'] = meigen['title']
        data['body'] = meigen['body']
        data['words'] = words
        meigenData.append(data)
        if data['id'] % 50 == 0:
            print('id = %d' % data['id'])

    with open('meigenWords.bin', 'wb') as f:
        pickle.dump(meigenData, f)

    with open('meigenWords.csv', mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        for data in meigenData:
            writer.writerow(data["words"])

    print("pickels updated. meigen count:[%s]" % len(meigenData))


def update_json(url='http://horesase-boys.herokuapp.com/meigens.json'):
    """
    名言辞書を最新化します
    - 名言辞書をURLもしくはローカルから取得
    - 名言辞書の形態素解析
    """

    # 名言辞書の更新
    try:
        print("downloading json...")
        r = urllib.request.urlopen(url)
    except:
        print('Could not download json\nCheck Internet Connetcion...')
        return
    with open("meigens.json", "wb") as f:
        f.write(r.read())

    ts = os.stat("meigens.json").st_mtime
    print("file[meigens.json] updated:[%s]" % datetime.fromtimestamp(ts))

    # デシリアライズと形態素解析
    make_pickle_from_json('meigens.json')


def test_func_1(sentence):
    print("input: [%s]" % sentence)
    print("output:[%s]" % breakdown_into_validwords(sentence))


def test_func_2():
    update_json()


if __name__ == '__main__':
    """
    単独実行時の処理
    - テストしたい処理を記述する
    """
    #test_func_1('今日はいい天気ですね')
    test_func_2();


