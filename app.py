from flask import (Flask, jsonify, render_template, request, make_response, url_for)
from datetime import datetime
import math

app = Flask(__name__, template_folder="templates")

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

tasks = [
    {
        'id': 1,
        'TicketNo': u'hbdm123',
        'DateTimeStamp': datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
        'AutomationServiceAccount': u'xyz',
        'CallingAPIKey': u'abcd123',
        'APIType': u'rest',
        'Source': u'jklm',
        'TargetDevices': u'jekhwb',
        'AutomationName': u'Genp',
        'Status': u'Not Done',
        'ExecutionTime': 200
    },
    {
        'id': 2,
        'TicketNo': u'hbdm456',
        'DateTimeStamp': datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
        'AutomationServiceAccount': u'zxc',
        'CallingAPIKey': u'abcd345',
        'APIType': u'rest',
        'Source': u'jklmn',
        'TargetDevices': u'jek',
        'AutomationName': u'Genpa',
        'Status': u'Done',
        'ExecutionTime': 400
    }
]

@app.route('/')
def home():
    return render_template('home.html')

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', CAK=task['CallingAPIKey'], _external=True)  # absolute address
        else:
            new_task[field] = task[field]
    return new_task

page_limit = 5

@app.route('/api/telemetry/task', methods=['GET'])
#http://localhost:5000/api/telemetry/task?CAK=abcd&pno=1
def get_task():  # with partial search
    CAK = (request.args.get('CAK', None))
    pno = int(request.args.get('pno', 1))
    if not CAK:
        if len(tasks[(pno - 1) * page_limit:(pno - 1) * page_limit + page_limit]):
            return jsonify({'Total Tasks': len(tasks), 'No. of pages': math.ceil(len(tasks)/page_limit)},
                           {'tasks': [make_public_task(task) for task in tasks[(pno - 1) * page_limit:(pno - 1) * page_limit + page_limit]]})
        return jsonify({'Error: ': 'No tasks to show.'})

    CAK = str(request.args.get('CAK',None))
    ts = []
    for t in tasks:
        for i in range(0, len(t['CallingAPIKey'])):
            if CAK == t['CallingAPIKey'][0:i + 1]:
                ts.append(t)
                break
    if len(ts[(pno-1)*page_limit:(pno-1)*page_limit+page_limit]):
        return jsonify({'Total Tasks': len(ts), 'No. of pages': math.ceil(len(ts)/page_limit)},
                       {'tasks': [make_public_task(task) for task in ts[(pno-1)*page_limit:(pno-1)*page_limit+page_limit]]})
    return jsonify({'Error: ': 'No tasks to show.'})

@app.route('/api/telemetry/task', methods=['POST'])
def create_task():
    task = {'id': (tasks[-1]['id'] + 1) if len(tasks) else 1,
            'TicketNo': request.json.get('TicketNo', ""),
            'DateTimeStamp': request.json.get('DateTimeStamp', ""),
            'AutomationServiceAccount': request.json.get('AutomationServiceAccount', ""),
            'CallingAPIKey': request.json.get('CallingAPIKey', ""),
            'APIType': request.json.get('APIType', ""),
            'Source': request.json.get('Source', ""),
            'TargetDevices': request.json.get('TargetDevices', ""),
            'AutomationName': request.json.get('AutomationName', ""),
            'Status': request.json.get('Status', ""),
            'ExecutionTime': request.json.get('ExecutionTime', 0)
            }
    tasks.append(task)
    return jsonify({'task': tasks[-1]}), 201

if __name__ == '__main__':
    app.run(debug=True)
