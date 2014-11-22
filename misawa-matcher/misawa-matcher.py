# -*- coding: utf-8 -*-
import json
import csv
import os
import sys
import nltk
import pickle
import webbrowser
import unicodedata
from subprocess import Popen, PIPE

'''
コマンドライン引数から読み込んだ文章で類似度検索
mecabへのパスが通っている必要あり（pythonバインディングは利用せず）

参考:mecabのpythonバインディングのインストールは次でイケる(mac, linux)
pip install mecab-python3
'''


def breakdown_into_validwords(string):
    '''
    mecabを使って形態素解析
    '''
    ret_list = []

    if string == '' or not(isinstance(string, str)):
        return ret_list

    string = string.replace("\n", "")

    with open('.input.txt', 'w') as f:
        # 適当な例外処理
        try:
            f.write(string)
        except:
            return ret_list

    # 無理やりmecabで処理
    p = Popen(["mecab", "-Ochasen", ".input.txt"], stdout=PIPE)
    while 1:
        line = p.stdout.readline()[:-1]
        if os.name == 'nt':
            line = line.decode('cp932')
        else:
            line = line.decode('utf-8')

        if line[:3] == "EOS":
            break
        if not line:
            continue

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

    p.wait()
    return ret_list


def make_pickle_from_json(fn='../meigens.json'):
    '''
    meigens.jsonを形態素解析し、辞書型の配列を作成・pickle保存
    '''
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
        data['url'] = meigen['image']
        data['chr'] = meigen['character']
        data['title'] = meigen['title']
        data['meigen'] = meigen['body']
        data['words'] = words
        meigenData.append(data)
        print('id = %d' % data['id'])

    with open('meigenWords.bin', 'wb') as f:
        pickle.dump(meigenData, f)

    with open('meigenWords.csv', mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        for data in meigenData:
            writer.writerow(data["words"])


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

    tweetWords = breakdown_into_validwords(tweet)

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
