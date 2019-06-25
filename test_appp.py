import appp  # the app that we have to test
import unittest
import json
import random
import string
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
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['tasks']) <= appp.Page_Limit, msg='Tasks shown on page exceed page limit')

    def test_get_few(self):          #test get few tasks (by matching Calling_API_Key) functionality of api
        CAK= str(randomStrings(random.randint(1, 10))) # random generated CallingAPIKey to pass  as url parameter
        response = self.app.get(BASE_URL+'?Calling_API_Key='+CAK+'&Page=1&Page_Limit=10')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn(CAK, data['tasks'][0:appp.Page_Limit]['CallingAPIKey'], msg="CallingAPIKey of results don't match passed Calling_API_Key")
        self.assertTrue(len(data['tasks']) <= appp.Page_Limit, msg='Tasks shown on page exceed page limit')
        self.assertTrue(len(data['tasks']) <= len(appp.tasks), msg='Number of Tasks shown exceed existing tasks')
        self.assertTrue(len(appp.ts) <= len(appp.tasks), msg='Number of Tasks matching exceed existing tasks')

    def test_empty_list(self):        #see if tasks list was empty, then newly created task should get id 1
        self.app.post(BASE_URL, data={'TicketNo.': 'hubds2', 'CallingAPIKey': 'jdoe'}, content_type='application/json')
        rv = self.app.get(BASE_URL)
        self.assertTrue(int(rv.data['tasks']['id']) == 1, msg = 'Empty list test Failed')

    def test_post(self):
        #test if correct error is returned if 'id' is provided while posting(id is automatically assigned so not needed to pass)
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
        self.assertEqual(data["Error: "], "id of the task is automatically assigned, no need to provide it")

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
        data = json.loads(response2.get_data())
        self.assertEqual(data['task']['id'], len(appp.tasks), msg='Wrong id given to newly created task')
        self.assertEqual(len(data['task']), len(appp.tasks[0]), msg = 'Newly created task does not have right number of fields')


    def tearDown(self):
        appp.tasks = self.backup_items     # reset appp.tasks to initial state


if __name__ == '__main__':
    unittest.main()