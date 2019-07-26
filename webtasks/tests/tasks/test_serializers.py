from django.test import TestCase
from tasks.models import Task
from tasks.serializers import TaskDetailSerializer
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.utils.timezone import utc
import logging

logger = logging.getLogger("serializers")


class TaskSeriaizerTest(TestCase):

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


    def test_serialized_username_priority(self):
        """
        get the expected keys first_name, last_name and task_priority
        with the expected value from the serialized objects.
        """

        task1 = Task.objects.get(pk=1)
        task2 = Task.objects.get(pk=2)

        serialized_task1 = TaskDetailSerializer(task1, many=False).data
        serialized_task2 = TaskDetailSerializer(task2, many=False).data

        serialized_keys = sorted(list(serialized_task1.keys()))
        expected_keys = sorted(['task_priority', 'first_name', 'last_name'])
        
        logger.debug("serialized_task1 object: {}".format(serialized_task1))
        logger.debug("serialized_task2 object: {}".format(serialized_task2))

        # the keys from the serializers should match what is expected
        self.assertEquals(serialized_keys, expected_keys)

        # the first_name and last_name should match what is expected
        self.assertEquals(serialized_task1['first_name'], 'foo1')
        self.assertEquals(serialized_task1['last_name'], 'bar1')
        self.assertEquals(serialized_task2['first_name'], 'foo2')
        self.assertEquals(serialized_task2['last_name'], 'bar2')

        # the task_priority should should match what is expected.
        self.assertEquals(serialized_task1['task_priority'], 'L')
        self.assertEquals(serialized_task2['task_priority'], 'H')


    @classmethod
    def tearDownClass(cls):
        """ delete all objects created """

        Task.objects.all().delete()
        User.objects.all().delete()
        logger.debug("tearDownClass {}".format(cls.__name__))
        
