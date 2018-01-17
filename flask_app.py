#!flask/bin/python
#coding=utf8
from flask import Flask, jsonify, json
from flask import abort
import jieba
import xlrd
# reload(sys)
# sys.setdefaultencoding('utf8')


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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



@app.route('/api/question/<string:question>', methods=['GET'])
def get_answer(question):
    data = xlrd.open_workbook('20171013.xlsx')
    table = data.sheet_by_name('questions')
    nrows = table.nrows
    ncols = table.ncols
    #index = question.find(u' ')
    #if index >= len(question):
    #    return
    #sub_question = question[(index + 1):]
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
        union_set = set(question_list).union(set(seg_list))
        union_list = list(union_set)
        intersection_list = list(union_set ^ (set(question_list)^set(seg_list)))
        question_list_len = len(question_list)
        union_list_len = len(union_list)
        intersection_list_len = len(intersection_list)
        if intersection_list_len * 100 >= question_list_len * 60:
            temp = float(intersection_list_len) / float(question_list_len)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
