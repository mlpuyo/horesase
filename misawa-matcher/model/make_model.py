# coding: utf-8

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim import corpora, models, similarities
dictionary = corpora.Dictionary.load_from_text('jawiki_wordids.txt.bz2')
corpus = corpora.MmCorpus('jawiki_tfidf.mm') # comes from the first tutorial, "From strings to vectors"

# lsiモデルを使う
# lsi300 = models.LsiModel(corpus, num_topics=300, id2word=dictionary)
# lsi300.save("lsi300.model")
#
# lsi100 = models.LsiModel(corpus, num_topics=100, id2word=dictionary)
# lsi100.save("lsi100.model")

# ldaモデルを使う
# lda300 = models.LdaModel(corpus, num_topics=300, id2word=dictionary)
# lda300.save("lda300.model")
#
# lda100 = models.LdaModel(corpus, num_topics=100, id2word=dictionary)
# lda100.save("lda100.model")

lda200 = models.LdaModel(corpus, num_topics=200, id2word=dictionary)
lda200.save("lda200.model")
