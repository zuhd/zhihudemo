#coding=utf8

import pymysql
import time
import datetime
import re
import string
import os
import sys
import warnings

class Database:
    def __init__(self, host, user, passwd, name='db_hegui', port=3306):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.name = name
        self.port = port

    def query_question(self):
        start = time.clock()
        result = {}
        try:
            conn_dest = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd,  db=self.name, port=self.port, use_unicode=1, charset='utf8')
            cur_dest = conn_dest.cursor()
            # 需要status >=6 的数据才能满足条件
            cur_dest.execute('select id, content from t_question')
            now_row_dest = int(cur_dest.rowcount)
            for i in range(now_row_dest):
                fetch_one = cur_dest.fetchone()
                result[fetch_one[0]] = fetch_one[1]

            # end for
            conn_dest.commit()
            cur_dest.close()
            conn_dest.close()
            end = time.clock()
            print('cost time %d S' % (end - start))
            return result
        except pymysql.Error, e:
            conn_dest.rollback()
            print("mysql error")
            print(e)

