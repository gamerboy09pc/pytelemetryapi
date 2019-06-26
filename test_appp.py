import appp  # the app that we have to test
import unittest
import json
import random
import string
import pprint
from datetime import datetime
from copy import deepcopy

BASE_URL = 'http://127.0.0.1:5000/api/telemetry/task'


def randomStrings(length):                # a method to create random strings to put in tasks
    """Generate a random string of letters, digits and special characters of passed length"""
    allowed = string.printable
    return ''.join(random.choice(allowed) for i in range(length))


class MyTestCase1(unittest.TestCase):

    def setUp(self):
        self.backup_items = deepcopy(appp.tasks)  # create backup of appp.tasks - no references
        self.app = appp.app.test_client()
        self.app.testing = True

    def test_get_all(self):              #test get all tasks functionality of api
        response = self.app.get(BASE_URL)
        data = json.loads(response.get_data())
        pprint.pprint(data)
        pprint.pprint(len(data))
        # test to check response code returned by get request
        self.assertEqual(response.status_code, 200)
        pprint.pprint(len(data[1]['tasks'][0]))
        self.assertTrue(len(data[1]['tasks']) <= appp.Page_Limit, msg='Tasks shown on page exceed page limit')
        # test to check page limit constraint

    def test_get_few(self):          # test get few tasks (by matching Calling_API_Key) functionality of api

    # first we will post few tasks , adding their CallingAPIKey's to a list, from which we will pass to the get function
        x = len(appp.tasks)  # length of tasks list before post calls
        y = 1000  # how many tasks to post
        CAKlist = [] # list to store generated CallingAPIKey's

        for i in range(0, y):  # repeat test for many post calls
            # see if correct status code is returned, correct id assigned and right number of fields in newly created task
            task2 = {"TicketNo": str(randomStrings(random.randint(1, 5))),
                     "DateTimeStamp": datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
                     "AutomationServiceAccount": str(randomStrings(random.randint(1, 5))),
                     "CallingAPIKey": "abcd"+str(randomStrings(random.randint(1,2))), # all CallingAPIKey begin with abcd
                     "APIType": str(randomStrings(random.randint(1, 5))),
                     "Source": str(randomStrings(random.randint(1, 5))),
                     "TargetDevices": str(randomStrings(random.randint(1, 5))),
                     "AutomationName": str(randomStrings(random.randint(1, 5))),
                     "Status": u"Done",
                     "ExecutionTime": random.randint(1, 1000)
                     }
            response2 = self.app.post(BASE_URL,
                                      data=json.dumps(task2),
                                      content_type='application/json')

            self.assertEqual(response2.status_code, 201)
            # test for status code returned by post
            data = json.loads(response2.get_data())
            #pprint.pprint(data)
            CAKlist.append(data['task']['CallingAPIKey'])
            # pprint.pprint(data)


        pprint.pprint(CAKlist)
        # randomly selected CallingAPIKey from CAKlist to pass as url parameter
        randomCAK = CAKlist[random.randint(0, y)]
        response = self.app.get(BASE_URL+'?Calling_API_Key='+randomCAK+'&Page=1&Page_Limit=10')
        data = json.loads(response.get_data())
        #pprint.pprint(data)

        self.assertEqual(response.status_code, 200)
        for i in range(0,len(data[1]['tasks'])):
            self.assertIn(randomCAK, data[1]['tasks'][i]['CallingAPIKey'] , msg="CallingAPIKey of results don't match passed Calling_API_Key")
        self.assertTrue(len(data[1]) <= appp.Page_Limit, msg='Tasks shown on page exceed page limit')
        self.assertTrue(len(data[1]) <= len(appp.tasks), msg='Number of Tasks shown exceed existing tasks')
        self.assertTrue(len(appp.ts) <= len(appp.tasks), msg='Number of Tasks matching exceed existing tasks')

    def test_empty_list(self):        # test if tasks list was empty, then newly created task should get id 1

        self.backup_items = deepcopy(appp.tasks) # backup tasks list

        for i in range(len(appp.tasks)-1,-1,-1):
           appp.tasks.pop(i)                   # empty tasks list
        pprint.pprint(appp.tasks)
        task = { "TicketNo": str(randomStrings(random.randint(1, 7))),
                 "DateTimeStamp": datetime.now().strftime(("%Y-%m-%d %H:%M:%S")),
                 "AutomationServiceAccount": str(randomStrings(random.randint(1, 10))),
                 "CallingAPIKey": str(randomStrings(random.randint(1, 10))),
                 "APIType": str(randomStrings(random.randint(1, 5))),
                 "Source": str(randomStrings(random.randint(1, 5))),
                 "TargetDevices": str(randomStrings(random.randint(1, 7))),
                 "AutomationName": str(randomStrings(random.randint(1, 7))),
                 "Status": u"Not Done",
                 "ExecutionTime": random.randint(1, 1000)
                 }
        response = self.app.post(BASE_URL, data=json.dumps(task), content_type='application/json') # post a new task to empty tasks list

        self.assertTrue(appp.tasks[0]['id'] == 1, msg='Empty list test Failed')  # check if id 1 was assigned to the new task
        appp.tasks = self.backup_items  # restore original tasks list

    def test_post(self):

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
                                 content_type='application/json')

            self.assertEqual(response1.status_code, 200)
            data = json.loads(response1.get_data())
            #pprint.pprint(data)
            self.assertEqual(data["Error: "], "id of the task is automatically assigned, no need to provide it")

        x=len(appp.tasks) # length of tasks list before post calls
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
                   "Status": u"Done",
                   "ExecutionTime": random.randint(1, 1000)
                   }
           response2 = self.app.post(BASE_URL,
                                 data=json.dumps(task2),
                                 content_type='application/json')
           self.assertEqual(response2.status_code, 201)
           #test for status code returned by post
           data = json.loads(response2.get_data())
           #pprint.pprint(data)

           self.assertEqual(data['task']['id'], len(appp.tasks), msg='Wrong id given to newly created task')
           # test for id assigned to new task

           self.assertEqual(len(data['task']), len(appp.tasks[0]), msg = 'Newly created task does not have right number of fields')
           # test for number of fields in new task

        self.assertEqual(data['task']['id'],x+y,msg='id of last task not correct')
        # test for id of last task, x+y should be equal to id of the last task created

    def tearDown(self):
        appp.tasks = self.backup_items     # reset appp.tasks to initial state


if __name__ == '__main__':
    unittest.main()