from flask import (Flask, jsonify, render_template, request, make_response, url_for)
from datetime import datetime
import math

app = Flask(__name__, template_folder="templates")

# global variables
Page_Limit = 5 # limit on number of tasks shown per page, can be changed by passing as url parameter in get functions
Page = 1 # the page to display for the results returned by get functions
ts=[]  # list to store tasks matching specified CallingAPIKey in get function

@app.errorhandler(400)                        #handle error 400 neatly, give json response
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)                        #handle error 404 neatly, give json response
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

tasks = [                 #list to store tasks of dictionary type
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
def home():                                       #home page
    return render_template('home.html')


def make_public_task(task):           # replace 'id' field of task with uri of the task
                                    # uri also allows acts as a link to all other tasks with the same CallingAPIKey
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', Calling_API_Key=task['CallingAPIKey'], _external=True)  # _external=True gives absolute address
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/api/telemetry/task', methods=['GET'])
# http://localhost:5000/api/telemetry/task?Calling_API_Key=abcd&Page=1&Page_Limit=10
def get_task():  # get all tasks or specific tasks by Calling_API_Key parameter with partial search, Page and Page_Limit parameters for pagination

    global Page_Limit
    global Page
    Calling_API_Key = request.args.get('Calling_API_Key', None)
    Page = request.args.get('Page', 1)
    Page_Limit = request.args.get('Page_Limit', 5)

    if not str(Page_Limit).isdigit() or int(Page_Limit) < 1 :
        return jsonify({'Error: ': 'Page Limit has to be an integer and cannot be less than 1. (Maximum 100)'})
    if int(Page_Limit)>100:                   # Max 100 tasks per page
        (Page_Limit)=100
    Page_Limit=int(Page_Limit)
    if int(Page) < 1 or not str(Page).isdigit() :
        return jsonify({'Error: ': 'Page Number has to be an integer and cannot be less than 1.'})
    Page=int(Page)

    # to get all tasks when Calling_API_Key is not specified but only few at a time = Page_Limit
    if not Calling_API_Key:
        if Page > math.ceil(len(tasks) / Page_Limit) :
            return jsonify({'Error: ': 'No tasks to show for the specified page number. '
                                       'Enter page number between 1 to '+ str(math.ceil(len(tasks)/Page_Limit))})
        if len(tasks[(Page - 1) * Page_Limit:(Page - 1) * Page_Limit + Page_Limit]):
            return jsonify({'Total Tasks': len(tasks), 'Number of Pages': math.ceil(len(tasks)/Page_Limit),
                            'Page Limit (maximum : 100)': Page_Limit} ,
                           {'tasks': [make_public_task(task) for task in tasks[(Page - 1) * Page_Limit:(Page - 1) * Page_Limit + Page_Limit]]})
        return jsonify({'Error: ': 'No tasks to show.'})

    # to get all tasks with the specified Calling_API_Key - max tasks per page = Page_Limit
    Calling_API_Key = str(request.args.get('Calling_API_Key',None))
    global ts                             # global list to store matching tasks with the specified Calling_API_Key
    for i in range(len(ts) - 1, -1, -1):  # empty ts[] as it may have search results of previous calls
        ts.pop(i)
    for t in tasks:
        for i in range(0, len(t['CallingAPIKey'])):
            if Calling_API_Key == t['CallingAPIKey'][0:i + 1]:
                ts.append(t)
                break
    if(len(ts)):
        if Page > math.ceil(len(ts) / Page_Limit):
            return jsonify({'Error: ': 'No tasks to show for the specified page number.'})
    if len(ts[(Page-1)*Page_Limit:(Page-1)*Page_Limit+Page_Limit]):
        return jsonify({'Total Tasks': len(ts), 'No. of pages': math.ceil(len(ts)/Page_Limit), 'Page Limit (maximum : 100)': Page_Limit},
                       {'tasks': [make_public_task(task) for task in ts[(Page-1)*Page_Limit:(Page-1)*Page_Limit+Page_Limit]]})
    return jsonify({'Error: ': 'No tasks to show for the specified CallingAPIKey'})


@app.route('/api/telemetry/task', methods=['POST'])
def create_task():       #post task - values of fields optional
    if 'id' in request.json:
        return jsonify({'Error: ': "id of the task is automatically assigned, no need to provide it"})
    if 'ExecutionTime' in request.json and not str(request.json.get('ExecutionTime')).isdigit():
        return jsonify({'Error: ': "Execution Time can only be an integer type"})
    # new task to be added to tasks list
    task = {'id': (tasks[-1]['id'] + 1) if len(tasks) else 1,    # id of last task + 1 if tasks list is not empty else 1
            'TicketNo': request.json.get('TicketNo', ""),
            'DateTimeStamp': request.json.get('DateTimeStamp', datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))),
            'AutomationServiceAccount': request.json.get('AutomationServiceAccount', ""),
            'CallingAPIKey': request.json.get('CallingAPIKey', ""),
            'APIType': request.json.get('APIType', ""),
            'Source': request.json.get('Source', ""),
            'TargetDevices': request.json.get('TargetDevices', ""),      #get optional parameter values - default values also specified
            'AutomationName': request.json.get('AutomationName', ""),
            'Status': request.json.get('Status', ""),
            'ExecutionTime': request.json.get('ExecutionTime', 0)
            }
    tasks.append(task)
    return jsonify({'task': tasks[-1]}), 201         #show newly created task and return success code

if __name__ == '__main__':
    app.run(debug=True)                 #debug mode, switch off before deploying
