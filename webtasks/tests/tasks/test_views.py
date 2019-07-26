from django.test import TestCase
from rest_framework.test import APIClient
from tasks.models import Task
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.utils.timezone import utc
import logging

logger = logging.getLogger("views")
API_PATH = 'http://127.0.0.1:8001/tasks/'


class TasksDetailsListViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        create tasks objects with different start and end dates to be 
        used in the tests of this class. also create two users.
        """

        
        logger.debug("setup {} started".format(cls.__name__))

        user1 =	User.objects.create_user(
            first_name="foo1",
            last_name="bar1",
            email="foobar@bla.com",
            username="fooobaar1234")

        user2 =	User.objects.create_user(
            first_name="foo2",
            last_name="bar2",
            email="foobar2@bla.com",
            username="fooobaar12345")

        current_date = datetime.now(timezone.utc)
        start_10_day_before = current_date - timedelta(days=10)
        start_7_day_before = current_date - timedelta(days=7)
        start_2_day_before = current_date - timedelta(days=2)
        start_4_day_after = current_date + timedelta(days=4)

        end_3_day_before = current_date - timedelta(days=3)
        end_2_day_after = current_date + timedelta(days=2)
        end_5_day_after = current_date + timedelta(days=5)
        
        Task.objects.bulk_create(
            [
                Task(id=1,
                     name="task a completed",
                     owner=user1,
                     priority="L",
                     start=start_10_day_before,
                     end=end_3_day_before,
                ),
                Task(id=2,
                     name="task b scheduled",
                     owner=user2,
                     priority="H",
                     start=start_4_day_after ,
                     end=end_5_day_after,
                ),
            ]
        )

        cls.api_client = APIClient(enforce_csrf_checks=True)


    def test_get_task_details_json_200(self):
        """ 
        make a get request to the task api and expect to get back a 
        json response with http status 200.
        """

        api = API_PATH + 'task/1/'
        response = self.api_client.get(api)
        content_type = response._headers['content-type'][1]
        status_code = response.status_code
        
        
        logger.debug("response: {}".format(response))
        logger.debug("response content-type: {}".format(content_type))
        logger.debug("response status_code: {}".format(status_code))

        self.assertEquals(status_code, 200)
        self.assertEquals(content_type, 'application/json')

    def test_get_task_details_content_200(self):
        """ 
        make a get request to the task api and expect to get back a 
        json response with the expected content keys and values.
        """

        api = API_PATH + 'task/2/'
        response = self.api_client.get(api)
        status_code = response.status_code
        content = response.json()

        response_content_keys = sorted(list(content.keys()))
        expected_keys = sorted(['task_priority', 'first_name', 'last_name'])
        
        
        logger.debug("response: {}".format(response))
        logger.debug("response content: {}".format(content))

        self.assertEquals(status_code, 200)
        self.assertTrue(content)
        self.assertEquals(response_content_keys, expected_keys)
        self.assertTrue(content.get('task_priority', False) == 'H')
        self.assertTrue(content.get('first_name', False) == 'foo2')
        self.assertTrue(content.get('last_name', False) == 'bar2')

    def test_get_task_not_found_404(self):
        """ 
        make a get request to the task api with a non existing id, 
        expect to get back http status 404 not found.
        """

        api = API_PATH + 'task/20/'
        response = self.api_client.get(api)
        status_code = response.status_code
        content = response.json()

        logger.debug("response: {}".format(response))
        logger.debug("response content: {}".format(content))

        self.assertEquals(status_code, 404)
        self.assertTrue(content)

    def test_get_page_not_found_404(self):
        """ 
        make a get request to the task api with a non existing api, 
        expect to get back http status 404 not found.
        """

        api = API_PATH + 'task/20/'
        response = self.api_client.get(api)
        status_code = response.status_code
        content = response.json()

        logger.debug("response: {}".format(response))
        logger.debug("response content: {}".format(content))

        self.assertEquals(status_code, 404)
        self.assertTrue(content)

        
    @classmethod
    def tearDownClass(cls):
        """ delete all objects created """

        Task.objects.all().delete()
        User.objects.all().delete()
        logger.debug("tearDownClass {}".format(cls.__name__))
        
        


class TasksListViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        create tasks objects with different start and end dates to be 
        used in the tests of this class. also create two users.
        """

        
        logger.debug("setup {} started".format(cls.__name__))

        user1 =	User.objects.create_user(
            first_name="foo1",
            last_name="bar1",
            email="foobar@bla.com",
            username="fooobaar1234")

        current_date = datetime.now(timezone.utc)
        start_10_day_before = current_date - timedelta(days=10)
        start_7_day_before = current_date - timedelta(days=7)
        start_2_day_before = current_date - timedelta(days=2)
        start_4_day_after = current_date + timedelta(days=4)

        end_3_day_before = current_date - timedelta(days=3)
        end_2_day_after = current_date + timedelta(days=2)
        end_5_day_after = current_date + timedelta(days=5)
        
        Task.objects.bulk_create(
            [
                Task(
                     name="task a",
                     owner=user1,
                     priority="L",
                     start=start_7_day_before,
                     end=end_3_day_before,
                ),
                Task(
                     name="task b ",
                     owner=user1,
                     priority="H",
                     start=start_4_day_after,
                     end=end_5_day_after,
                ),
                Task(name="task c ",
                     owner=user1,
                     priority="H",
                     start=start_10_day_before,
                     end=end_2_day_after,
                ),
                Task(
                     name="task d ",
                     owner=user1,
                     priority="H",
                     start=start_2_day_before,
                     end=end_5_day_after,
                ),
            ]
        )

        cls.api_client = APIClient(enforce_csrf_checks=True)


    def test_get_all_tasks_html_200(self):
        """ 
        make a get request to the task view and expect to get back a 
        an html response with http status 200.
        """

        api = API_PATH + 'alltasks/'
        response = self.api_client.get(api)
        content_type = response._headers['content-type'][1]
        status_code = response.status_code
        
        
        logger.debug("response: {}".format(response))
        logger.debug("response content-type: {}".format(content_type))
        logger.debug("response status_code: {}".format(status_code))

        self.assertEquals(status_code, 200)
        self.assertEquals(content_type, 'text/html; charset=utf-8')
        self.assertTrue(True)


    def test_get_index_html_200(self):
        """ 
        make a get request to the index task view and expect to get back a 
        an html response with http status 200.
        """

        api = API_PATH
        response = self.api_client.get(api)
        content_type = response._headers['content-type'][1]
        status_code = response.status_code
        
        
        logger.debug("response: {}".format(response))
        logger.debug("response content-type: {}".format(content_type))
        logger.debug("response status_code: {}".format(status_code))

        self.assertEquals(status_code, 200)
        self.assertEquals(content_type, 'text/html; charset=utf-8')
        self.assertTrue(True)

        
    @classmethod
    def tearDownClass(cls):
        """ delete all objects created """

        Task.objects.all().delete()
        User.objects.all().delete()
        logger.debug("tearDownClass {}".format(cls.__name__))
        
        
