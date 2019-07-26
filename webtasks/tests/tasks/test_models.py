from django.test import TestCase
from tasks.models import Task
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.utils.timezone import utc
import logging


logger = logging.getLogger("task")


class TaskTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        create tasks objects with different start and end dates to be 
        used in the tests of this class.
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
                Task(id=3,
                     name="task c running",
                     owner=user1,
                     priority="M",
                     start= start_2_day_before,
                     end=end_2_day_after,
                ),
                Task(id=4,
                     name="task d running",
                     owner=user1,
                     priority="H",
                     start=start_2_day_before,
                     end=end_5_day_after,
                ),
                Task(id=5,
                     name="task e multi-runs",
                     owner=user1,
                     priority="H",
                     start=start_2_day_before,
                     end=end_5_day_after,
                ),
                Task(id=6,
                     name="task f Idle",
                     owner=user1,
                     priority="L",
                     start=start_2_day_before,
                     end=end_5_day_after,
                ),
                Task(id=7,
                     name="task g with all subtask completed",
                     owner=user1,
                     priority="H",
                     start=start_2_day_before,
                     end=end_5_day_after,
                ),

            ]

        )


        Task(name="subtask e.1 running",
             owner=user1,
             priority="L",
             start=start_10_day_before,
             end=end_2_day_after,
             parent_task=Task.objects.get(pk=5)
        ).save()

        Task(name="subtask e.2 running",
             owner=user2,
             priority="H",
             start=start_10_day_before ,
             end=end_5_day_after,
             parent_task=Task.objects.get(pk=5)
        ).save()

        Task(name="subtask e.3 completed",
             owner=user1,
             priority="H",
             start=start_10_day_before ,
             end=end_3_day_before,
             parent_task=Task.objects.get(pk=5)
        ).save()
        
        Task(name="task f.1 completed",
            owner=user1,
            priority="M",
            start= start_10_day_before,
            end=end_3_day_before,
            parent_task=Task.objects.get(pk=6)
        ).save()

        Task(name="task f.2 scheduled",
             owner=user1,
             priority="H",
             start=start_4_day_after,
             end=end_5_day_after,
             parent_task=Task.objects.get(pk=6)
        ).save()

        Task(name="task g.1 completed",
             owner=user1,
             priority="M",
             start= start_10_day_before,
             end=end_3_day_before,
             parent_task=Task.objects.get(pk=7)
        ).save()

        Task(name="task g.2 completed",
             owner=user1,
             priority="H",
             start=start_7_day_before,
             end=end_3_day_before,
             parent_task=Task.objects.get(pk=7)
        ).save()

        
    def test_get_tasks_with_statuses_scheduled(self):
        """ 
        fetch all statuses of the tasks and expect one task to be 
        Complete = 5, Running = 4, Multi-Runs = 1, Idle = 1 and Scheduled = 2
        """

        tasks = Task.objects.all()

        task_status = [task.status for task in tasks]
        logger.debug("tasks statuses are: {}".format(task_status))

        self.assertEquals(task_status.count('Scheduled'), 2)
        self.assertEquals(task_status.count('Complete'), 6)
        self.assertEquals(task_status.count('Running'), 4)
        self.assertEquals(task_status.count('Multi-Runs'), 1)
        self.assertEquals(task_status.count('Idle'), 1)
        

    def test_duration_tasks_without_subtasks(self):
        """ 
        fetch all tasks that have no subtasks, take their start and end datetime and 
        duration and match the result with what is expected in minutes.
        """

        tasks = Task.objects.filter(parent_task__isnull=True)
        task_durations = [task.duration for task in tasks]

        logger.debug("tasks durations are: {}".format(task_durations))

        task1 = {
            'start': tasks[0].start,
            'end': tasks[0].end,
            'duration': tasks[0].duration
        }

        task2 = {
            'start': tasks[1].start,
            'end': tasks[1].end,
            'duration': tasks[1].duration
        }

        task3 = {
            'start': tasks[2].start,
            'end': tasks[2].end,
            'duration': tasks[2].duration
        }


        task4 = {
            'start': tasks[3].start,
            'end': tasks[3].end,
            'duration': tasks[3].duration
        }

        task1_duration = (task1['end'] - task1['start']).total_seconds() / 60
        task2_duration = (task2['end'] - task2['start']).total_seconds() / 60
        task3_duration = (task3['end'] - task3['start']).total_seconds() / 60
        task4_duration = (task4['end'] - task4['start']).total_seconds() / 60

        self.assertEquals(task1_duration, task1['duration'])
        self.assertEquals(task2_duration, task2['duration'])
        self.assertEquals(task3_duration, task3['duration'])
        self.assertEquals(task4_duration, task4['duration'])


    def test_status_multi_runs(self):
        """ 
        get the task ith id 5 which has two subtasks running and one 
        complete. expect its status to be multi-runs.
        """

        task = Task.objects.get(pk=5)
        subtasks = Task.objects.filter(parent_task__id=task.id)

        logger.debug("parent task status: {}".format(task.status))
        logger.debug("parent subtask1 status: {}".format(subtasks[0].status))
        logger.debug("parent subtask2 status: {}".format(subtasks[1].status))
        logger.debug("parent subtask3 status: {}".format(subtasks[2].status))
        
        # two subtasks have the status Running and one Complete
        self.assertTrue(subtasks[0].status == 'Running')
        self.assertTrue(subtasks[1].status == 'Running')
        self.assertTrue(subtasks[2].status == 'Complete')

        # the parent task status is therefor Multi-runs
        self.assertTrue(task.status == 'Multi-Runs')

    def test_status_Idle(self):
        """ 
        get the task ith id 6 which has two subtasks, completed and 
        scheduled. expect its status to be Idle.
        """

        task = Task.objects.get(pk=6)
        subtasks = Task.objects.filter(parent_task__id=task.id)

        logger.debug("parent task status: {}".format(task.status))
        logger.debug("parent subtask1 status: {}".format(subtasks[0].status))
        logger.debug("parent subtask2 status: {}".format(subtasks[1].status))
        
        # two subtasks with one is Scheduled and one Complete
        self.assertTrue(subtasks[0].status == 'Complete')
        self.assertTrue(subtasks[1].status == 'Scheduled')

        # the parent task status is therefor Idle
        self.assertTrue(task.status == 'Idle')


    def test_parent_status_same_as_all_subtask_status(self):
        """ 
        validate that if the subtasks have the same status, that status
        is the parent task status. So get the task ith id 7 which has
        two subtasks, both have the status complete. expect parent 
        task status to be complete.
        """

        task = Task.objects.get(pk=7)
        subtasks = Task.objects.filter(parent_task__id=task.id)

        logger.debug("parent task status: {}".format(task.status))
        logger.debug("parent subtask1 status: {}".format(subtasks[0].status))
        logger.debug("parent subtask2 status: {}".format(subtasks[1].status))
        
        # two subtasks with the same status Complete
        self.assertTrue(subtasks[0].status == 'Complete')
        self.assertTrue(subtasks[1].status == 'Complete')

        # the parent task status is therefor Complete
        self.assertTrue(task.status == 'Complete')


        
        
    def test_save_start_and_end_date_of_tasks_with_subtasks(self):
        """ 
        fetch a tasks which has subtasks and get see that the start
        date matches the earliest start date of the subtasks and the 
        end date matches the last end date of a subtask. unless it's 
        own start date is already earlier and an date is later.
        """

        task_f = Task.objects.get(pk=6)
        subtasks_f = Task.objects.filter(parent_task__id=task_f.id)

        logger.debug("task_f startdate: {} - enddate: {}".format(task_f.start, task_f.end))
        logger.debug("subtask_f.1 start: {} - enddate: {}".format(subtasks_f[0].start, subtasks_f[0].end))
        logger.debug("subtask_f.2 start: {} - enddate: {}".format(subtasks_f[1].start, subtasks_f[1].end))

        # subtask f1 has the earliest start date and f2 has the latest
        # end date. so the start and end date of the parent task f
        # should be between equal them
        
        self.assertEquals(task_f.start, subtasks_f[0].start)
        self.assertEquals(task_f.end, subtasks_f[1].end)
        
        
    @classmethod
    def tearDownClass(cls):
        """ delete all objects created """

        Task.objects.all().delete()
        User.objects.all().delete()
        logger.debug("tearDownClass {}".format(cls.__name__))
        
