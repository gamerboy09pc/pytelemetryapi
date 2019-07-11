from flask import (Flask, jsonify, render_template, request, make_response, url_for)  # installed through pip
from datetime import datetime
import math
import random
import string
import pyodbc  # installed through pip
import pprint # prettyprint
from flask_httpauth import HTTPBasicAuth  # installed through pip

app = Flask(__name__, template_folder="templates")

'''........................................authentication block start......................................'''

auth = HTTPBasicAuth()

userN = 'pc'   # username
passW = 'pcp'  # password


@auth.get_password              #provides basic http authentication for get and post
# in postman go to authorization tab, select Basic Auth and put username password there
def get_password_and_key(username):
    """ Simple text-based authentication """
    if username == userN:
        return passW
    else:
        return None


@auth.error_handler
def unauthorized():
    #Return a 403 instead of a 401 to prevent browsers from displaying the default auth dialog
    return make_response(jsonify({'message': 'Unauthorized Access'}), 403)

'''......................................authentication block end........................................'''


# global variables
Page_Limit = 5 # limit on number of tasks shown per page, can be changed by passing as url parameter in get functions
Page = 1 # the page to display for the results returned by get functions
ts=[]  # list to store tasks matching specified CallingAPIKey in get function


'''...................................http error handling block start................................'''


@app.errorhandler(400)                        #handle error 400 neatly, give json response
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)                        #handle error 404 neatly, give json response
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


'''...................................http error handling block end................................'''


'''...................................sql server connection block start................................'''


server = 'LAPTOP-96DA7F8K'
database = 'telemetry'
username = 'sa'
password = 'mssqlparth'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database
                      +';UID='+username+';PWD='+ password)
#print(type(cnxn))
cursor = cnxn.cursor()


'''...................................sql server connection block end................................'''

'''tasks = [                 # sample data for list to store tasks of dictionary type
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
'''

tasks=[] # a list that will temporarily store data fetched from database, will be converted to json and displayed

@app.route('/')
def home():                                       #home page
    return render_template('home.html')


def make_public_task(task):           # replace 'id' field of task with uri of the task
                                    # uri also allows acts as a link to all other tasks with the same CallingAPIKey
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', Calling_API_Key=task['CallingAPIKey'], _external=True)
            # _external=True gives absolute address
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/api/telemetry/task', methods=['GET'])
@auth.login_required
# http://localhost:5000/api/telemetry/task?Calling_API_Key=abcd&Page=1&Page_Limit=10
def get_task():  # get all tasks or specific tasks by Calling_API_Key parameter with partial search,
                 # Page and Page_Limit parameters for pagination

    cursor.execute("select max(id) from dbo.tasks;")
    Number_of_tasks = [x for x in cursor.fetchone()][0] # check if database is empty
    if not Number_of_tasks:
        return jsonify({'Error: ': 'No tasks in database'})
    global tasks
    for i in range(len(tasks) - 1, -1, -1):  # empty tasks[] as it may have search results of previous calls
        tasks.pop(i)
    global Page_Limit
    global Page
    Calling_API_Key = request.args.get('Calling_API_Key', None)
    Page = request.args.get('Page', 1)
    Page_Limit = request.args.get('Page_Limit', 5)
    #print(Calling_API_Key)

    if not str(Page_Limit).isdigit() or int(Page_Limit) < 1 :
        return jsonify({'Error: ': 'Page Limit has to be an integer and cannot be less than 1. (Maximum 100)'})
    if int(Page_Limit)>100:                   # Max 100 tasks per page(adjust according to need)
        (Page_Limit)=100
    Page_Limit=int(Page_Limit)
    if int(Page) < 1 or not str(Page).isdigit() :
        return jsonify({'Error: ': 'Page Number has to be an integer and cannot be less than 1.'})
    Page=int(Page)

    # to get all tasks - when Calling_API_Key is not specified but only few at a time = Page_Limit
    if not Calling_API_Key:
        cursor.execute("use telemetry;")
        cursor.execute("select max(id) from dbo.tasks;")
        Number_of_tasks = [x for x in cursor.fetchone()][0]  # number of tasks in database
        if Page > math.ceil(Number_of_tasks / Page_Limit) :
            return jsonify({'Error: ': 'No tasks to show for the specified page number. '})
        cursor.execute("select * from tasks where id between "
                       +str((Page - 1) * Page_Limit)+" and "+str((Page - 1) * Page_Limit + Page_Limit)+";")
        row = cursor.fetchone()

        while row:
            #print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
            tasks.append({'id': row[0],
                          'TicketNo': row[1],
                          'DateTimeStamp': row[2],
                          'AutomationServiceAccount': row[3],
                          'CallingAPIKey': row[4],
                          'APIType': row[5],
                          'Source': row[6],
                          'TargetDevices': row[7],
                          'AutomationName': row[8],
                          'Status': row[9],
                          'ExecutionTime': row[10]})
            row = cursor.fetchone()

        if len(tasks):
            return jsonify({'Total Tasks': Number_of_tasks, 'Number of Pages': math.ceil(Number_of_tasks/Page_Limit),
                            'Page Limit (maximum : 100)': Page_Limit},
                           {'tasks': [make_public_task(task) for task in tasks]})
        return jsonify({'Error: ': 'No tasks to show.'})

    # to get all tasks with the specified Calling_API_Key - max tasks per page = Page_Limit
    # to send url special characters like & and = as parameter, you have to percent-encode them
    # example -  & should be sent as %26
    Calling_API_Key = str(request.args.get('Calling_API_Key',None))
    global ts                             # global list to store matching tasks with the specified Calling_API_Key
    for i in range(len(ts) - 1, -1, -1):  # empty ts[] as it may have search results of previous calls
        ts.pop(i)

    if '%' in Calling_API_Key or '[' or '_' in Calling_API_Key:

        esc_char = random.choice(string.punctuation)
        while esc_char in Calling_API_Key:              # generate random escape character not present in CallingAPIKey
            esc_char = random.choice(string.punctuation)
        print(esc_char)
        Calling_API_Key=Calling_API_Key.replace("%",esc_char+"%")
        Calling_API_Key = Calling_API_Key.replace("[", esc_char+"[")
        Calling_API_Key = Calling_API_Key.replace("_", esc_char+"_")
        #print(Calling_API_Key)

        cursor.execute("select count(CallingAPIKey) from tasks where CallingAPIKey like '" + Calling_API_Key
                       + "%' escape '" + esc_char + "';")
        matched_results = cursor.fetchone()[0]
        cursor.execute("select * from tasks where CallingAPIKey like '" + Calling_API_Key + "%'" +
                       " escape '"+esc_char+"' order by id OFFSET " + str((Page - 1) * Page_Limit) + " rows fetch first " +
                       str(Page_Limit) + " rows only" + ";")
        #print(Calling_API_Key)

    else:

        cursor.execute(
            "select count(CallingAPIKey) from tasks where CallingAPIKey like '" + Calling_API_Key + "%' ;")
        matched_results = cursor.fetchone()[0]
        cursor.execute("select * from tasks where CallingAPIKey like '" + Calling_API_Key + "%'" +
                       " order by id OFFSET " + str((Page - 1) * Page_Limit) + " rows fetch first " +
                       str(Page_Limit) + " rows only" + ";")

    row = cursor.fetchone()

    while row:
        ts.append({'id': row[0],
                      'TicketNo': row[1],
                      'DateTimeStamp': row[2],
                      'AutomationServiceAccount': row[3],
                      'CallingAPIKey': row[4],
                      'APIType': row[5],
                      'Source': row[6],
                      'TargetDevices': row[7],
                      'AutomationName': row[8],
                      'Status': row[9],
                      'ExecutionTime': row[10]})
        row = cursor.fetchone()


    if len(ts):
        if Page > math.ceil(len(ts) / Page_Limit):
            return jsonify({'Error: ': 'No tasks to show for the specified page number. '})
    if len(ts[(Page-1)*Page_Limit:(Page-1)*Page_Limit+Page_Limit]):
        return jsonify({'Matched Results': matched_results, 'No. of pages': math.ceil(len(ts)/Page_Limit),
                        'Page Limit (maximum : 100)': Page_Limit},
                       {'tasks': [make_public_task(task) for task in ts[(Page-1)*Page_Limit:(Page-1)*Page_Limit+Page_Limit]]}
                       )
    return jsonify({'Error: ': 'No tasks to show for the specified CallingAPIKey'})


@app.route('/api/telemetry/task', methods=['POST'])
@auth.login_required
def create_task():       #post task - values of fields optional, just one needs to be passed to avoid bad request error
    if request.json:
        if 'id' in request.json:
          return jsonify({'Error: ': "id of the task is automatically assigned, no need to provide it"})
    if 'ExecutionTime' in request.json and not str(request.json.get('ExecutionTime')).isdigit():
        return jsonify({'Error: ': "Execution Time can only be an integer type"})

    cursor.execute("insert into dbo.tasks(Ticket_Number,Date_time,Automation_Service_account,CallingAPIKey,APIType,"
                   "Source_,Target_Devices,Automation_Name,Status_,Execution_Time) values(?,?,?,?,?,?,?,?,?,?)",
                   request.json.get('TicketNo', ""), datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
                   request.json.get('AutomationServiceAccount', ""),request.json.get('CallingAPIKey', ""),
                   request.json.get('APIType', ""),request.json.get('Source', ""),
                   request.json.get('TargetDevices', ""),request.json.get('AutomationName', ""),
                   request.json.get('Status', ""),request.json.get('ExecutionTime', "")
                   )
    cnxn.commit()

    cursor.execute("use telemetry;")
    cursor.execute("select count(id) from dbo.tasks;")
    Number_of_tasks = [x for x in cursor.fetchone()][0]
    cursor.execute("select * from tasks where id = (select max(id) from dbo.tasks)")
    row = cursor.fetchone() # get this newly posted task from database to display
    # new task to be added to tasks list
    task = ({'id': row[0],
             'TicketNo': row[1],
             'DateTimeStamp': row[2],
             'AutomationServiceAccount': row[3],
             'CallingAPIKey': row[4],
             'APIType': row[5],
             'Source': row[6],
             'TargetDevices': row[7],
             'AutomationName': row[8],
             'Status': row[9],
             'ExecutionTime': row[10]})

    return jsonify({'task': task}), 201         #show newly created task and return success code


if __name__ == '__main__':
    app.run(debug=True)                 #debug mode, switch off before deploying
