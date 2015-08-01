#! /bin/bash
cd /home/ec2-user/horesase/misawa-matcher
date > date.txt
/usr/local/bin/python3 horesase_bot.py lsi300 model/lsi300.model model/jawiki_wordids.txt.bz2
date >> date.txt
# /usr/local/bin/python3 horesase_bot.py doc2vec model/d2v.model
