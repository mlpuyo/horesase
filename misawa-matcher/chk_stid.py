#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import sys
import logging
import datetime
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ID_DUMP_FN = "data/stidDic.bin"
SDATE = datetime.datetime.utcnow() - datetime.timedelta(hours=30)
EDATE = datetime.datetime.utcnow() - datetime.timedelta(hours=4.5)

def main():
    with open(ID_DUMP_FN, 'rb') as f:
        try:
            stid_dic = pickle.load(f)
        except:
            logger.error('empty pickle file', exc_info=True)

    logger.info("SDATE: %s" % SDATE)
    logger.info("EDATE: %s" % EDATE)

    for k, v in stid_dic.copy().items():
        # SDATE以前のツイートは削除
        if v["created_at"] < SDATE:
            logger.info("deleting: %s" % v["created_at"])
            del stid_dic[k]

        # EDATE以降のツイートは削除
        if v["created_at"] > EDATE:
            logger.info("deleting: %s" % v["created_at"])
            del stid_dic[k]

    with open(ID_DUMP_FN, 'wb') as f:
        pickle.dump(stid_dic, f)

if __name__ == '__main__':
    main()
