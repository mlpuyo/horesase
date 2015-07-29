
# coding: utf-8

# In[2]:

#!/usr/bin/env python

from __future__ import with_statement

import os
import numpy as np
from gensim import utils, matutils
from gensim.models import doc2vec

from logging import getLogger
logger = getLogger(__name__)

datapath = lambda fname: os.path.join('data', fname)


# In[14]:

def myhashfxn(obj):
    return hash(obj) % (2 ** 32)


# In[15]:

model = doc2vec.Doc2Vec(hashfxn=myhashfxn)
model = model.load('data/d2v.model')


# In[34]:

def extract_word(words, model):
    doc = []
    if len(words) == 1:
        try:
            model[words]
        except KeyError:
            return []
        return words

    for w in words:
        try:
            model[w]
        except KeyError:
            continue
        doc.append(w)
    return doc


# In[36]:

doc1 = extract_word(["近代" ], model)
doc2 = extract_word(["現代", "おかず"], model)

r = model.n_similarity(doc1, doc2)
print(r)
