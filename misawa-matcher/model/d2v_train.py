#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

import os
import numpy as np
from gensim import utils, matutils
from gensim.models import doc2vec

from logging import getLogger
logger = getLogger(__name__)

module_path = os.path.dirname(__file__)  # needed because sample data files are located in the same folder
datapath = lambda fname: os.path.join(module_path, '', fname)


class WikiCorpus(object):
    def __init__(self, string_tags=False):
        self.string_tags = string_tags

    def _tag(self, i):
        return i if not self.string_tags else '_*%d' % i

    def __iter__(self):
        with open(datapath('out4dvec.cor'), 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                yield doc2vec.TaggedDocument(utils.simple_preprocess(line), [self._tag(i)])

list_corpus = list(WikiCorpus())

sentences = [
        ['human', 'interface', 'computer'],
        ['survey', 'user', 'computer', 'system', 'response', 'time'],
        ['eps', 'user', 'interface', 'system'],
        ['system', 'human', 'system', 'eps'],
        ['user', 'response', 'time'],
        ['trees'],
        ['graph', 'trees'],
        ['graph', 'minors', 'trees'],
        ['graph', 'minors', 'survey']
    ]

sentences = [doc2vec.TaggedDocument(words, [i]) for i, words in enumerate(sentences)]

def test_load_mmap():
    """Test storing/loading the entire model."""
    model = doc2vec.Doc2Vec(sentences, min_count=1)

    # test storing the internal arrays into separate files
    model.save('test.d2vmodel', sep_limit=0)
    # self.models_equal(model, doc2vec.Doc2Vec.load(testfile()))

def test_training():
    """Test doc2vec training."""
    corpus = WikiCorpus()
    # model = doc2vec.Doc2Vec(size=100, min_count=2, iter=20)
    # model = doc2vec.Doc2Vec(hashfxn=lambda obj: hash(obj) % (2 ** 32))
    model = doc2vec.Doc2Vec(hashfxn=myhashfxn)
    # model.train_lbls = False
    model.build_vocab(corpus)
    model.train(corpus)
    model.save('d2v.model', sep_limit=0)

    # build vocab and train in one step; must be the same as above
    # model2 = doc2vec.Doc2Vec(corpus, size=100, min_count=2, iter=20)

def myhashfxn(obj):
    return hash(obj) % (2 ** 32)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)

    test_training()
    # model = doc2vec.Doc2Vec(sentences, min_count=1, hashfxn=myhashfxn)
    # model = doc2vec.Doc2Vec.load('data/d2v.model')
    # doc1 = ["近代" ]
    # doc2 = ["国内"]
    # r = model.n_similarity(doc1, doc2)
    # logger.info(r)
