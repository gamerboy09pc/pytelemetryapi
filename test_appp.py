import appp  # the app that we have to test
import unittest
import json
import random
import string
import pprint
import base64
import pyodbc
import urllib
import logging
from datetime import datetime
from copy import deepcopy

BASE_URL = 'http://127.0.0.1:5000/api/telemetry/task'

'''...................................logging setup block start................................'''

logging.basicConfig(filename="test.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.info(" test_appp STARTED ")

'''...................................logging setup block end................................'''

'''...................................sql server connection block start................................'''


server = 'LAPTOP-96DA7F8K'
database = 'telemetry'
username = 'sa'
password = 'mssqlparth'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database
                      +';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()


'''...................................sql server connection block end................................'''



def randomStrings(length):                # a method to create random strings to put in tasks
    """Generate a random string of letters, digits and special characters of passed length"""
    allowed = string.printable
    return ''.join(random.choice(allowed) for i in range(length))

def randomCharacter():         # a method to create random character to append after 'abcd' in CallingAPIKey in get_few
  """Generate a random character from letters, digits and special characters
  (whitespace character not allowed except blankspace)"""
  c = random.choice(string.printable)
  while c in string.whitespace :
    if c == " ":
        return c
    c = random.choice(string.printable)
  return c

class MyTestCase1(unittest.TestCase):

    def setUp(self):
        self.backup_items = deepcopy(appp.tasks)  # create backup of appp.tasks - no references
        self.app = appp.app.test_client()
        self.app.testing = True

    def test_get_all(self):              #test get all tasks functionality of api

        logger.info(datetime.now().strftime(("%Y-%m-%d %H:%M:%S")) + " test_get_all RUN ")
        response = self.app.get(BASE_URL, headers={'Authorization': 'Basic ' + base64.b64encode(bytes(appp.userN+':' +appp.passW,'ascii')).decode('ascii')})
        data = json.loads(response.get_data())
        #pprint.pprint(data)
        #pprint.pprint(len(data))
        # test to check response code returned by get request

        self.assertEqual(response.status_code, 200, msg='Response code Test Failed')
        print('test_get_all - response code - Test passed')

        #pprint.pprint(len(data[1]['tasks'][0]))
        self.assertTrue(len(data[1]['tasks']) <= appp.Page_Limit, msg='Test Failed - Tasks shown on page exceed page limit')
        print('test_get_all - Page Limit constraint - Test passed')
        # test to check page limit constraint
        cursor.execute("use telemetry;")
        cursor.execute("select count(id) from dbo.tasks;")
        Number_of_tasks = [x for x in cursor.fetchone()][0]
        print(Number_of_tasks)
        self.assertTrue(len(data[1]['tasks']) <= appp.Page_Limit,
                        msg='Test Failed - Tasks shown on page exceed tasks actually in database')
        print('test_get_all - No extra tasks - Test passed')


    def test_get_few(self):  # test get few tasks (by matching Calling_API_Key) functionality of api

        logger.info(datetime.now().strftime(("%Y-%m-%d %H:%M:%S")) + " test_get_few RUN ")
        # first we will post few tasks , adding their CallingAPIKey's to a list, from which we will pass to the get function
        cursor.execute("use telemetry;")
        cursor.execute("truncate table dbo.tasks;")
        cnxn.commit()
        y = 1000  # how many tasks to post
        CAKlist = []  # list to store generated CallingAPIKey's

        for i in range(0, y):  # repeat test for many post calls
            # see if correct status code is returned, correct id assigned and right number of fields in newly created task
            task2 = {"TicketNo": str(randomStrings(random.randint(1, 5))),
                     "DateTimeStamp": datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
                     "AutomationServiceAccount": str(randomStrings(random.randint(1, 5))),
                     "CallingAPIKey": "abcd" + str(randomCharacter()),
        # all CallingAPIKey begin with abcd and are appended with a non-whitespace character(blankspace allowed though)
                     "APIType": str(randomStrings(random.randint(1, 5))),
                     "Source": str(randomStrings(random.randint(1, 5))),
                     "TargetDevices": str(randomStrings(random.randint(1, 5))),
                     "AutomationName": str(randomStrings(random.randint(1, 5))),
                     "Status": u"Done",
                     "ExecutionTime": random.randint(1, 1000)
                     }
            response2 = self.app.post(BASE_URL,
                                      data=json.dumps(task2),
                                      content_type='application/json', headers=
                                      {'Authorization': 'Basic ' + base64.b64encode(
                                          bytes(appp.userN + ':' + appp.passW, 'ascii')).decode('ascii')})

            self.assertEqual(response2.status_code, 201, msg='Response code Test Failed')
            # test for status code returned by post
            data = json.loads(response2.get_data())
            # pprint.pprint(data)
            CAKlist.append(data['task']['CallingAPIKey'])
            # pprint.pprint(data)


        x=1000  # number of times the test will be done
        for i in range(0,x):
            # pprint.pprint(CAKlist)
            # randomly selected CallingAPIKey from CAKlist to pass as url parameter
            randomCAK = CAKlist[random.randint(0, y)]
            #print(randomCAK)
            # print("\n url encoded " + randomCAK + " -> " + urllib.parse.quote(randomCAK))
            response = self.app.get(
                BASE_URL + '?Calling_API_Key=' + urllib.parse.quote(randomCAK) + '&Page=1&Page_Limit=10',
                headers={'Authorization': 'Basic ' + base64.b64encode(bytes(appp.userN + ':' + appp.passW, 'ascii')).decode(
                    'ascii')})
            data = json.loads(response.get_data())
            # pprint.pprint(data)

            cursor.execute("select count(id) from dbo.tasks;")
            Number_of_tasks = [x for x in cursor.fetchone()][0]
            self.assertEqual(response.status_code, 200, msg='Response code Test Failed')
            print('test_get_few - response code - Test passed')
            for i in range(0, len(data[1]['tasks'])):
                self.assertTrue(randomCAK.lower() in (data[1]['tasks'][i]['CallingAPIKey']).lower(),
                                msg="Test Failed - CallingAPIKey of results don't match passed Calling_API_Key")
            '''
            lower() is used as sql is case insensitive it returns all that match irrespective of lower or upper characters, 
            but python does not regard them as equals
            for eg abcdM not equal to abcdm in python but sql returns abcdM as a match to abcdm 
            '''
            print('test_get_few - CallingAPIKey match - Test passed')
            self.assertTrue(len(data[1]) <= appp.Page_Limit, msg='Test Failed - Tasks shown on page exceed page limit')
            print('test_get_few - Page Limit - Test passed')
            self.assertTrue(len(data[1]) <= Number_of_tasks,
                            msg='Test Failed - Number of Tasks shown exceed existing tasks')
            print('test_get_few - Number of result Tasks shown - Test passed')
            self.assertTrue(len(appp.ts) <= Number_of_tasks,
                            msg='Test Failed - Number of Tasks matching exceed existing tasks')
            print('test_get_few - Number of result Tasks less than existing tasks - Test passed')


    def test_empty_table(self):        # test if tasks list was empty, then newly created task should get id 1

        logger.info(datetime.now().strftime(("%Y-%m-%d %H:%M:%S")) + " test_empty_table RUN ")
        cursor.execute("use telemetry;")
        cursor.execute("truncate table dbo.tasks;")
        cnxn.commit()
        #pprint.pprint(appp.tasks)
        task = {"TicketNo": str(randomStrings(random.randint(1, 7))),
                "DateTimeStamp": datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
                "AutomationServiceAccount": str(randomStrings(random.randint(1, 10))),
                "CallingAPIKey": str(randomStrings(random.randint(1, 10))),
                "APIType": str(randomStrings(random.randint(1, 5))),
                "Source": str(randomStrings(random.randint(1, 5))),
                "TargetDevices": str(randomStrings(random.randint(1, 7))),
                "AutomationName": str(randomStrings(random.randint(1, 7))),
                "Status": "Done" if random.randint(0,1) == 0 else "Not Done",
                "ExecutionTime": random.randint(1, 1000)
               }
        response = self.app.post(BASE_URL, data=json.dumps(task), content_type='application/json', headers=
        {'Authorization': 'Basic ' + base64.b64encode(bytes(appp.userN+':'+appp.passW,'ascii')).decode('ascii')})
        # post a new task to empty tasks list
        cursor.execute("select max(id) from dbo.tasks;")
        new_id = [x for x in cursor.fetchone()][0]
        self.assertTrue(new_id == 1, msg='Test Failed - Empty table test Failed')
        # check if id 1 was assigned to the new task
        print('test_empty_list - id=1 for Empty Table - Test passed')

    def test_post(self):

        logger.info(datetime.now().strftime(("%Y-%m-%d %H:%M:%S")) + " test_post RUN ")
        cursor.execute("use telemetry;")
        cursor.execute("truncate table dbo.tasks;")
        cnxn.commit()
        #test if correct error is returned if 'id' is provided while posting(id is automatically assigned so not required to pass)
        for i in range(0,100): # repeat the test a number of times
            task1 = {"id": 1,
                     "TicketNo": str(randomStrings(random.randint(1,7))),
                     "DateTimeStamp": datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
                     "AutomationServiceAccount": str(randomStrings(random.randint(1,10))),
                     "CallingAPIKey": str(randomStrings(random.randint(1,10))),
                     "APIType": str(randomStrings(random.randint(1,5))),
                     "Source": str(randomStrings(random.randint(1,5))),
                     "TargetDevices": str(randomStrings(random.randint(1,7))),
                     "AutomationName": str(randomStrings(random.randint(1,7))),
                     "Status": u"Not Done",
                     "ExecutionTime": random.randint(1,1000)
                     }
            response1 = self.app.post(BASE_URL,
                                 data=json.dumps(task1),
                                 content_type='application/json', headers=
                                      {'Authorization': 'Basic ' + base64.b64encode(bytes(appp.userN+':'+appp.passW,'ascii')).decode('ascii')})

            self.assertEqual(response1.status_code, 200, msg='Response code Test Failed')

            data = json.loads(response1.get_data())
            #pprint.pprint(data)
            self.assertEqual(data["Error: "], "id of the task is automatically assigned, no need to provide it",
                             msg = 'Test Failed - Error doesnot match')
        print('test_post - correct Response Code returned by all posts(id test) - Test passed')
        print("test_post - check if error shown when 'id' parameter sent for all posts - Test passed")

        # length of tasks list before post calls
        y=1000 # how many times to repeat the test
        for i in range(0, y):  # repeat test for many post calls
          #see if correct status code is returned, correct id assigned and right number of fields in newly created task
           task2 = {"TicketNo": str(randomStrings(random.randint(1, 7))),
                   "DateTimeStamp": datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
                   "AutomationServiceAccount": str(randomStrings(random.randint(1, 10))),
                   "CallingAPIKey": str(randomStrings(random.randint(1, 10))),
                   "APIType": str(randomStrings(random.randint(1, 5))),
                   "Source": str(randomStrings(random.randint(1, 5))),
                   "TargetDevices": str(randomStrings(random.randint(1, 7))),
                   "AutomationName": str(randomStrings(random.randint(1, 7))),
                   "Status": "Done" if random.randint(0,1) == 0 else "Not Done",
                   "ExecutionTime": random.randint(1, 1000)
                   }
           response2 = self.app.post(BASE_URL,
                                 data=json.dumps(task2),
                                 content_type='application/json',  headers=
                                     {'Authorization': 'Basic ' + base64.b64encode(bytes(appp.userN+":"+appp.passW,'ascii')).decode('ascii')})
           self.assertEqual(response2.status_code, 201, msg='Response code Test Failed')

           #test for status code returned by post
           data = json.loads(response2.get_data())
           #pprint.pprint(data)

           cursor.execute("select max(id) from dbo.tasks;")
           new_id = [x for x in cursor.fetchone()][0]
           self.assertEqual(data['task']['id'], new_id, msg='Test Failed - Wrong id given to newly created task')
           # test for id assigned to new task
           cursor.execute("select * from dbo.tasks where id=1;")
           rows = cursor.fetchall()
           number_of_columns = len(rows[0])
           self.assertEqual(len(data['task']), number_of_columns, msg = 'Test Failed - Newly created task does '
                                                                        'not have right number of fields')
           # test for number of fields in new task

        print('test_post - correct Response Code returned by all posts - Test passed')
        print('test_post - correct Number of fields in all new tasks posted - Test passed')
        print('test_post - correct id assigned to all new task - Test passed')
        self.assertEqual(data['task']['id'],y,msg='Test Failed - id of last task not correct')
        # test for id of last task, y should be equal to id of the last task created
        print('test_post - id of last task posted correct(equal to number of tasks)  - Test passed')


    def tearDown(self):
        appp.tasks = self.backup_items  # reset appp.tasks to initial state


if __name__ == '__main__':
    unittest.main()
