# coding=utf8
import random

import pymysql
import time
import datetime
import re
import string
import os
import sys
import warnings

# Tip Type
from enum import Enum


class TipType(Enum):
    tip_question = (1 << 0)
    tip_answer = (1 << 1)
    tip_topic = (1 << 2)
    tip_knowledge = (1 << 3)
    tip_all = tip_question | tip_answer | tip_topic | tip_knowledge

class Database:
    def __init__(self, host, user, passwd, name='db_hegui', port=3306):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.name = name
        self.port = port

    def query(self, tip_type):
        if tip_type == 1:
            return self.query_question()
        if tip_type == 2:
            return self.query_answer()
        if tip_type == 4:
            return self.query_knowledge()
        if tip_type == 8:
            return self.query_topic()

    def query_question(self):
        start = time.clock()
        result = {}
        try:
            conn_dest = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.name,
                                        port=self.port, use_unicode=1, charset='utf8')
            cur_dest = conn_dest.cursor()
            # 需要status >=6 的数据才能满足条件
            cur_dest.execute('select id, content from t_question where deleted <= 0 and status >= 6')
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

    def query_answer(self):
        start = time.clock()
        result = {}
        try:
            conn_dest = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.name,
                                        port=self.port, use_unicode=1, charset='utf8')
            cur_dest = conn_dest.cursor()
            # 需要status >=6 的数据才能满足条件
            cur_dest.execute('select id, content from t_answer where deleted <= 0 and status >= 6')
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

    def query_knowledge(self):
        start = time.clock()
        result = {}
        try:
            conn_dest = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.name,
                                        port=self.port, use_unicode=1, charset='utf8')
            cur_dest = conn_dest.cursor()
            # 需要status >=6 的数据才能满足条件
            cur_dest.execute('select id, content from t_knowledge where deleted <= 0')
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

    def query_topic(self):
        start = time.clock()
        result = {}
        try:
            conn_dest = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.name,
                                        port=self.port, use_unicode=1, charset='utf8')
            cur_dest = conn_dest.cursor()
            # 需要status >=6 的数据才能满足条件
            cur_dest.execute('select id, description from t_topic where status = 1')
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


    def insert_question(self, uid, content):
        start = time.clock()
        try:
            conn_dest = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.name,
                                        port=self.port, use_unicode=1, charset='utf8')
            cur_dest = conn_dest.cursor()
            rand_int = random.randint(1, 100)
            now_time = time.localtime(time.time() - rand_int * 24 * 3600)
            str_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
            cur_dest.execute('insert into t_question (uid, content, status, anonymity, deleted, create_time) values (%s, %s, 7, 1, 0, %s)', (uid, content, str_time))
            cur_dest.execute('select id from t_question order by id desc limit 1')
            fetch_one = cur_dest.fetchone()
            question_id = fetch_one[0]
            conn_dest.commit()
            cur_dest.close()
            conn_dest.close()
            end = time.clock()
            print('cost time %d S' % (end - start))
            return question_id
        except pymysql.Error, e:
            conn_dest.rollback()
            print("mysql error")
            print(e)

    def insert_answer(self, uid, questionid, content):
        start = time.clock()
        try:
            conn_dest = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.name,
                                        port=self.port, use_unicode=1, charset='utf8')
            cur_dest = conn_dest.cursor()
            rand_int = random.randint(1, 100)
            now_time = time.localtime(time.time() - rand_int * 24 * 3600)
            str_time = time.strftime("%Y-%m-%d %H:%M:%S", now_time)
            cur_dest.execute('insert into t_answer (uid, question_id, content, status, anonymity, deleted, create_time) values (%s, %s, %s, 7, 1, 0, %s)', (uid, questionid, content, str_time))
            conn_dest.commit()
            cur_dest.close()
            conn_dest.close()
            end = time.clock()
            print('cost time %d S' % (end - start))
        except pymysql.Error, e:
            conn_dest.rollback()
            print("mysql error")
            print(e)
