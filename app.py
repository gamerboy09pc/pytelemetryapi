from flask import (Flask, jsonify, render_template, request, make_response)
from datetime import datetime

'''import Flask class. An instance of this class will be our WSGI application.'''

app = Flask(__name__, template_folder="templates")

'''Next we create an instance of this class. The first argument is
the name of the application’s module or package. If you are using a
single module (as in this example), you should use __name__ because
depending on if it’s started as application or imported as module
the name will be different ('__main__' versus the actual import name).
This is needed so that Flask knows where to look for templates,
static files, and so on.'''


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


tasks = [
    {
        'id': 1,
        'TicketNo': u'hbdm123',
        'datetimest': get_timestamp(),
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
        'datetimest': get_timestamp(),
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


# use the route() decorator to tell Flask
# what URL should trigger our function.'/'


'''#$ curl -i http://localhost:5000/api/telemetry/task/abcd123'''


@app.route('/api/telemetry/task/<string:CAK>', methods=['GET'])
def get_task(CAK):
    for t in tasks:
        if t['CallingAPIKey'] == CAK:
            return jsonify({'Task': t})
    return jsonify({'Error: ': 'No such task exists. Please specify correct CallingAPIKey.'})


'''#$ curl -i http://localhost:5000/api/telemetry/task'''


@app.route('/api/telemetry/task', methods=['GET'])
def get_alltasks():
    return jsonify({'tasks': tasks})


# $ curl -i -H "Content-Type: application/json" -X POST -d '{"TicketNo":"aghsg"}' http://localhost:5000/api/telemetry/task
# curl -i -H "Content-Type: application/json" -X POST -d "{"""TicketNo""":"""akjs"""}" http://localhost:5000/api/telemetry/task
@app.route('/api/telemetry/task', methods=['POST'])
def create_task():
    task = {'id': tasks[-1]['id'] + 1,
            'TicketNo': request.json.get('TicketNo',""),
            'datetimest': request.json.get('datetimest',""),
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



















