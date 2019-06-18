from flask import ( Flask, jsonify, render_template, request, make_response)
from datetime import datetime

'''import Flask class. An instance of this class will be our WSGI application.'''

app = Flask(__name__,template_folder="templates")

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
        'id':1,
        'TicketNo': u'hbdm123',
        'datetimest': get_timestamp(),
        'AutomationServiceAccount':u'xyz',
        'CallingAPIKey': u'abcd123',
        'APIType': u'rest', 
        'Source': u'jklm',
        'TargetDevices': u'jekhwb',
        'AutomationName': u'Genp',
        'Status': u'Not Done',
        'ExecutionTime': 200
    },
    {
        'id':2,
        'TicketNo': u'hbdm456',
        'datetimest': get_timestamp(),  
        'AutomationServiceAccount':u'zxc',
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


#use the route() decorator to tell Flask
#what URL should trigger our function.'/'


'''#$ curl -i http://localhost:5000/telemetry/api/1'''
@app.route('/telemetry/api/<string:CAK>', methods=['GET'])
def get_task(CAK):
    for t in tasks:
        if t['CallingAPIKey'] == CAK:
            return jsonify({'Task': t})
    return jsonify({'Error: ': 'No such task exists. Please specify correct CallingAPIKey.'})


'''#$ curl -i http://localhost:5000/telemetry/api/alltasks'''
@app.route('/telemetry/api/alltasks', methods=['GET'])
def get_alltasks():
    return jsonify({'Tasks': tasks})

if __name__ == '__main__':
    app.run(debug=True)



'''
#$ curl -i http://localhost:5000/telemetry/api/v1.0/tasks/2
@app.route('/telemetry/api/1.0/tasks/<int:tid>', methods=['GET'])
def get_task(tid):
    for t in tasks:
        if t['id'] == tid:
            return jsonify({'Task': t})
'''
          
''' alternate version of ^
#$ curl -i http://localhost:5000/telemetry/api/v1.0/tasks?tid=2
@app.route('/telemetry/api/1.0/tasks', methods=['GET'])
def get_task():
    if 'tid' in request.args:
        t_id = int(request.args['tid'])
        for t in tasks:
            if t['id'] == t_id:
                return jsonify({'Task': t})
    else:
        return "Error: No task id field provided. Please specify an task id."
'''


'''
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not vfound'}), 404)
'''


@app.route('/telemetry/api/posttask/<string:Tn>', methods=['POST'])
#$ curl -i -H "Content-Type: application/json" -X POST -d '{"TicketNo":"aghsg"}' http://localhost:5000/telemetry/api/posttask
#curl -i -H "Content-Type: application/json" -X POST -d "{"""TicketNo""":"""akjs"""}" http://localhost:5000/telemetry/api/posttask
def create_task(Tn):
    if (request.method == 'POST'):
        '''if not request.json or not 'Tn' in request.json:
            abort(400)
           else:
        '''
        task = {
        'id': tasks[-1]['id'] + 1,
        'TicketNo': request.json['Tn'],
        'AutomationServiceAccount': request.json.get('AutomationServiceAccount', ""),
        'CallingAPIKey': request.json.get('CallingAPIKey', ""),
        'APIType': request.json.get('APIType', ""), 
        'Source': request.json.get('Source', ""),
        'TargetDevices': request.json.get('TargetDevices', ""),
        'AutomationName': request.json.get('AutomationName', ""),
        'Status': request.json.get('Status', ""),
        'ExecutionTime': request.json.get('ExecutionTime', 0),
        }
        tasks.append(task)
        return jsonify({'Task': task}), 201
    return jsonify({'Error: ': ''})






























