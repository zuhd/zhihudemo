#!flask/bin/python
# coding=utf8
from flask import Flask, jsonify, json
from flask import abort
from redis_cache import Redis
import jieba
import xlrd
import models

# reload(sys)
# sys.setdefaultencoding('utf8')


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# app.config['mysql_host'] = '192.168.50.237'
app.config['mysql_host'] = '127.0.0.1'
app.config['mysql_user'] = 'root'
app.config['mysql_passwd'] = ''
# app.config['redis_host'] = '192.168.50.237'
app.config['redis_host'] = '10.30.206.10'
app.config['redis_port'] = 6379
app.config['ENABLE_REDIS_CACHE'] = 1
app.config['REDIS_CACHE_TIMEOUT'] = 600

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route('/')
def default():
    return 'hello flask'


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


def get_question_list(question, trim_space=False):
    question_list = []
    question_list.append(question)
    if trim_space:
        question_list = question.split(' ')
    return question_list


@app.route('/api/test', methods=['GET'])
def test():
    database = models.Database('192.168.50.237', 'root', '')
    database.query_question()
    return 'test'


@app.route('/api/tiptest/<string:tip>', methods=['GET'])
def get_tiptest(tip):
    data = xlrd.open_workbook('20171013.xlsx')
    table = data.sheet_by_name('questions')
    nrows = table.nrows
    split_list = get_question_list(tip, True)
    question_list = []
    for v in split_list:
        question_list_genertor = jieba.cut(v, cut_all=False)
        v_list = list(question_list_genertor)
        question_list = question_list + v_list
    rate = 0.0
    index = -1
    tip_list = []
    for i in range(nrows):
        seg_list_generator = jieba.cut(table.cell(i, 4).value, cut_all=False)
        seg_list = list(seg_list_generator)
        question_set = set(question_list)
        seg_set = set(seg_list)
        union_set = question_set.union(seg_set)
        union_list = list(union_set)
        intersection_list = list(union_set ^ (question_set ^ seg_set))
        question_list_len = len(question_list)
        union_list_len = len(union_list)
        intersection_list_len = len(intersection_list)
        question_set_len = len(question_set)
        if intersection_list_len * 100 >= question_set_len * 30:
            index = i
            temp_dict = {
                'question': table.cell(index, 4).value,
                'answer': table.cell(index, 5).value
            }
            tip_list.append(temp_dict)

    if len(tip_list) > 0:
        obj = dict(ok=True, code=1001, msg=u'查询成功', data=tip_list)
        return json.dumps(obj, ensure_ascii=False)
    else:
        obj = {
            'ok': True,
            'code': 1004,
            'msg': u'查询失败',
            'data': [
                {
                    'question': u'not found',
                    'answer': u'not found'
                }
            ]
        }
        return json.dumps(obj, ensure_ascii=False)


@app.route('/api/questiontest/<string:question>', methods=['GET'])
def get_answer_test(question):
    data = xlrd.open_workbook('20171013.xlsx')
    table = data.sheet_by_name('questions')
    nrows = table.nrows
    ncols = table.ncols
    # index = question.find(u' ')
    # if index >= len(question):
    #    return
    # sub_question = question[(index + 1):]
    # sub_question = question[6:]
    split_list = get_question_list(question, True)
    question_list = []
    for v in split_list:
        question_list_generator = jieba.cut(v, cut_all=False)
        v_list = list(question_list_generator)
        question_list = question_list + v_list
    rate = 0.0
    index = -1
    for i in range(nrows):
        seg_list_generator = jieba.cut(table.cell(i, 4).value, cut_all=False)
        seg_list = list(seg_list_generator)
        # 为了避免权重下降，同一个语意中也要去重
        question_set = set(question_list)
        seg_set = set(seg_list)
        union_set = question_set.union(seg_set)
        union_list = list(union_set)
        intersection_list = list(union_set ^ (question_set ^ seg_set))
        question_list_len = len(question_list)
        union_list_len = len(union_list)
        intersection_list_len = len(intersection_list)
        question_set_len = len(question_set)
        if intersection_list_len * 100 >= question_set_len * 60:
            temp = float(intersection_list_len) / float(question_set_len)
            if temp > rate:
                index = i
                rate = temp
    if index >= 0:
        # return table.cell(index, 5).value
        print table.cell(index, 4).value
        print table.cell(index, 5).value
        obj = {
            'ok': True,
            'code': 1001,
            'msg': u'查询成功',
            'data': [
                {
                    'question': table.cell(index, 4).value,
                    'answer': table.cell(index, 5).value
                }
            ]
        }
        return json.dumps(obj, ensure_ascii=False)
        # return jsonify(obj)
    else:
        obj = {
            'ok': True,
            'code': 1004,
            'msg': u'查询失败',
            'data': [
                {
                    'question': u'not found',
                    'answer': u'not found'
                }
            ]
        }
        return json.dumps(obj, ensure_ascii=False)


def get_tip_bypage(tip, pagenum, pagesize, limit):
    data = xlrd.open_workbook('20171013.xlsx')
    table = data.sheet_by_name('questions')
    # database = models.Database('192.168.50.237', 'root', '')
    nrows = table.nrows
    split_list = get_question_list(tip, True)
    question_list = []
    for v in split_list:
        question_list_genertor = jieba.cut(v, cut_all=False)
        v_list = list(question_list_genertor)
        question_list = question_list + v_list
    rate = 0.0
    index = -1
    # 默认的返回值
    obj = {
            'ok': True,
            'code': 1004,
            'msg': u'查询失败',
            'totals': 0,
            'data': [
                {
                    'id': 0,
                    'content': u'not found'
                }
            ]
        }
    tip_list = []
    question_set = set(question_list)
    redis_cache = Redis.connect(app.config['redis_host'], app.config['redis_port'])
    if app.config['ENABLE_REDIS_CACHE']:
        cache_data = Redis.get_data(redis_cache, question_set)
        if cache_data is not None:
            print('find obj in redis')
            tip_list = cache_data
            if 0 < limit < pagesize:
                pagesize = limit
            begin = pagesize * pagenum
            end = begin + pagesize
            if begin >= len(tip_list):
                return json.dumps(obj, ensure_ascii=False)

            if end >= len(tip_list):
                end = len(tip_list)

            sub_tip_list = tip_list[begin:end]
            obj = dict(ok=True, code=1001, msg=u'查询成功', totals=len(tip_list), data=sub_tip_list)
            return json.dumps(obj, ensure_ascii=False)

    database = models.Database(app.config['mysql_host'], app.config['mysql_user'], app.config['mysql_passwd'])
    if app.config['ENABLE_REDIS_CACHE']:
        result_dict = Redis.get_data(redis_cache, app.config['mysql_host'])
        if result_dict is not None:
            print('find result dict in redis')
        else:
            result_dict = database.query_question()
            Redis.set_data(redis_cache, app.config['mysql_host'], result_dict, app.config['REDIS_CACHE_TIMEOUT'])

    for i in result_dict:
        seg_list_generator = jieba.cut(result_dict[i], cut_all=False)
        seg_list = list(seg_list_generator)

        seg_set = set(seg_list)
        union_set = question_set.union(seg_set)
        union_list = list(union_set)
        intersection_list = list(union_set ^ (question_set ^ seg_set))
        question_list_len = len(question_list)
        union_list_len = len(union_list)
        intersection_list_len = len(intersection_list)
        question_set_len = len(question_set)

        if intersection_list_len * 100 >= question_set_len * 30:
            index = i
            temp_dict = {
                'id': i,
                'content': result_dict[i]
            }
            tip_list.append(temp_dict)

    if len(tip_list) > 0:
        if 0 < limit < pagesize:
            pagesize = limit
        begin = pagesize * pagenum
        end = begin + pagesize
        if begin >= len(tip_list):
            return json.dumps(obj, ensure_ascii=False)

        if end >= len(tip_list):
            end = len(tip_list)

        sub_tip_list = tip_list[begin:end]
        obj = dict(ok=True, code=1001, msg=u'查询成功', totals=len(tip_list), data=sub_tip_list)
        Redis.set_data(redis_cache, question_set, tip_list, app.config['REDIS_CACHE_TIMEOUT'])
        return json.dumps(obj, ensure_ascii=False)
    else:

        return json.dumps(obj, ensure_ascii=False)


@app.route('/api/tip/<string:tip>/<int:pagenum>/<int:pagesize>/<int:limit>', methods=['GET', 'POST'])
def get_tip(tip, pagenum, pagesize, limit):
    return get_tip_bypage(tip, pagenum, pagesize, limit)


@app.route('/api/question/<string:question>', methods=['GET'])
def get_answer(question):
    data = xlrd.open_workbook('20171013.xlsx')
    table = data.sheet_by_name('questions')
    database = models.Database(app.config['host'], app.config['user'], app.config['passwd'])
    result_dict = database.query_question()
    nrows = table.nrows
    ncols = table.ncols
    # index = question.find(u' ')
    # if index >= len(question):
    #    return
    # sub_question = question[(index + 1):]
    # sub_question = question[6:]
    split_list = get_question_list(question, True)
    question_list = []
    for v in split_list:
        question_list_generator = jieba.cut(v, cut_all=False)
        v_list = list(question_list_generator)
        question_list = question_list + v_list
    rate = 0.0
    index = -1
    for i in result_dict:
        seg_list_generator = jieba.cut(result_dict[i], cut_all=False)
        seg_list = list(seg_list_generator)
        # 为了避免权重下降，同一个语意中也要去重
        question_set = set(question_list)
        seg_set = set(seg_list)
        union_set = question_set.union(seg_set)
        union_list = list(union_set)
        intersection_list = list(union_set ^ (question_set ^ seg_set))
        question_list_len = len(question_list)
        union_list_len = len(union_list)
        intersection_list_len = len(intersection_list)
        question_set_len = len(question_set)
        if intersection_list_len * 100 >= question_set_len * 60:
            temp = float(intersection_list_len) / float(question_set_len)
            if temp > rate:
                index = i
                rate = temp
    if index >= 0:
        # return table.cell(index, 5).value
        print(result_dict[i])
        obj = {
            'ok': True,
            'code': 1001,
            'msg': u'查询成功',
            'data': [
                {
                    'id': index,
                    'content': result_dict[index]
                }
            ]
        }
        return json.dumps(obj, ensure_ascii=False)
        # return jsonify(obj)
    else:
        obj = {
            'ok': True,
            'code': 1004,
            'msg': u'查询失败',
            'data': [
                {
                    'id': 0,
                    'content': u'not found'
                }
            ]
        }
        return json.dumps(obj, ensure_ascii=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
