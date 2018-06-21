# coding=utf8
from flask_app import app
import random

import time
import xlrd
import models

def load_data():
    data = xlrd.open_workbook('list.xlsx')
    table = data.sheet_by_name('QA')
    nrows = table.nrows
    ncols = table.ncols
    id_xlsx = xlrd.open_workbook('id.xlsx')
    id_sheet = id_xlsx.sheet_by_name('ID')
    id_rows = id_sheet.nrows
    id_cols = id_sheet.ncols
    database = models.Database(app.config['mysql_host'],  app.config['mysql_user'],  app.config['mysql_passwd'] , "db_hegui")
    for i in range(nrows):
        if i > 0:
            rand_int = random.randint(0, id_rows - 1)
            question_uid = id_sheet.cell(rand_int, 1).value
            question_id = database.insert_question(question_uid, table.cell(i, 0).value)
            rand_int = random.randint(0, id_rows - 1)
            answer_uid = id_sheet.cell(rand_int, 1).value
            database.insert_answer(answer_uid, question_id, table.cell(i, 1).value)

load_data()
