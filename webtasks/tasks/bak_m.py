from django.db import models
from django.db.models import Max, Min
from datetime import datetime, timedelta, timezone
import logging


logger = logging.getLogger("task")

class User(models.Model):
    """ 
    User model who run or own tasks. The user's firstname and 
    lastname combined are the unique constrains. 
    """

    first_name = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        db_index=True,
        help_text="User's first name who will own a task",
    )
    
    last_name = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        db_index=True,
        help_text="User's last name",
    )

    class Meta:
        ordering = ['first_name', 'last_name']
        unique_together = (('first_name', 'last_name'),)
        verbose_name_plural = "User"

        
    def __str__(self):
        """ represent the model object when called """
        return "%s %s" % (self.first_name, self.last_name)


class Task(models.Model):
    """
    Task model represent a task. 
    """

    name = models.CharField(
        max_length=30,
        blank=False,
        null=False,
        db_index=True,
        help_text="The task name",
    )

    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=False,
        help_text="The task owner",
    )

    PRIORITIES = (
        ('L', 'Low'),
        ('M', 'Meduim'),
        ('H', 'High'),
    )

    STATUS_TYPE = [
            'Scheduled',
            'Running',
            'Complete',
            'Multi-Runs',
            'Idle',
        ]


    priority = models.CharField(
        max_length=1,
        blank=False,
        null=False,
        default='L',
        choices=PRIORITIES,
        help_text="the priority of a task",
    )

    start = models.DateTimeField(
        auto_now_add=False,
        null=False,
        blank=False,
        db_index=True,
        help_text="the start date and time of a task",
    )

    end = models.DateTimeField(
        auto_now_add=False,
        null=False,
        blank=False,
        help_text="the end date and time of a task",
    )

    
    # the task status property
    def _status(self):
        """
        returns the status of the task based on the start and end times
        of the taks and it's subtasks.
        there are three statuses defined for each task:
        a- Scheduled if the start timestamp is in future.
        b- Running if the current time is between start time and end 
           time.
        c- Complete if the end time has passed.
        if the task has subtasks, there will be two additional 
        statuses: 
        d- Multi-Runs if more than one child is running.
        e- Idle if one or more tasks are complete and one or more 
           tasks are scheduled but nothing is running at the moment.

        """

        total_subtasks = SubTask.objects.filter(parent_task__id=self.id).count()

        logger.debug("task id: {} has {} sub tasks".format(self.id, total_subtasks))
        logger.debug("taskid: {} - start: {} - end: {}".format(self.id, self.start, self.end))

        # if the task has subtasks, call get_task_with_subtask_status.
        # otherwise, call get_status
        if total_subtasks > 0:
            return self.get_task_with_subtask_status()

        else:
            return self.get_status(start_date=self.start, end_date=self.end)
            

    def get_task_with_subtask_status(self):
        """ 
        reads the status of each subtask. add them in a dict with the 
        name of the status as key and total occurance as value. 
        example: {'Complete': 2, 'Running': 5, 'Scheduled': 3}
        if Running > 1 then the status will be Multi-Runs.
        if Completed >= 1 and Scheduled >= 1 and Running == 0 then the
        status will be Idle
        if the dict contains one key, the status will be that key.  
        """

        
        logger.debug("has more than one subtask")
        subtasks = SubTask.objects.filter(parent_task__id=self.id)

        logger.debug("substasks: {}".format(subtasks))

        # create a tmp list to store the status of the subtasks.
        status_tmp = []
        for sub in subtasks:
            # loop through the subtasks and append their status to the
            # status_tmp list.
            status_tmp.append(sub.status)
            logger.debug("subtaskid: {} - status: {}".format(sub.id, sub.status))

        # create a dict of the statuses in the status_tmp list
        subtasks_status = {k:status_tmp.count(k) for k in status_tmp}
        logger.debug("subtasks statuses: {}".format(subtasks_status))

        
        if subtasks_status.get('Running', 0) > 1 :
            # if more than 1 tasks are running, return Running
            return self.STATUS_TYPE[3]
        
        elif subtasks_status.get(self.STATUS_TYPE[2], 0) > 0 and subtasks_status.get(self.STATUS_TYPE[0], 0) > 0 and subtasks_status.get(self.STATUS_TYPE[1], 0) == 0:
            # if there are one or more Complete subtask
            # AND one or more subtasks Scheduled
            # AND there are no Running tasks, then the status is Idle
            return self.STATUS_TYPE[4]

        elif len(subtasks_status.keys()) == 1:
            # if all the subtasks have the same status, use it 
            return [subtasks_status.keys()][0]
        else:
            # at the moment use a defualt value like Scheduled
            return self.STATUS_TYPE[0]


            
    def _duration(self):
        """
        return the minutes of the duration of the task from start
        to end.
        """

        # get the timedelta object and convert it to seconds  
        diff_delta = (self.end - self.start).total_seconds()
        duration_min = diff_delta / 60 # divide the sec by 60 to get the minutes        
        logger.debug("starttime: {} - endtime: {} => minutes: {}".format(self.start, self.end, diff_delta))

        return duration_min
    

    status = property(_status)
    duration = property(_duration)


    
    def get_status(self, start_date=datetime, end_date=datetime):
        """
        takes the start and end dates as parameters, compares them
        with each other and the current date. It will return the 
        one of the below statuses based on the comparison results.
        a- Scheduled if the start timestamp is in future.
        b- Running if the current time is between start time and end 
           time.
        c- Complete if the end time has passed.
        """

        current_date = datetime.now(timezone.utc)

        logger.debug("get_status start_date: {} - end_date: {} - current_date: {}".format(start_date, end_date, current_date))
        
        if start_date > current_date:
            return self.STATUS_TYPE[0]
        elif end_date < current_date:
            return self.STATUS_TYPE[2]
        elif start_date < current_date and end_date > current_date:
            return self.STATUS_TYPE[1]
        
    
    class Meta:
        ordering = (('start'),)
        verbose_name_plural = "Task"


    def __str__(self):
        """
        representation of the taks object.
        """

        return "task %s start time at %s and end time at %s" % (self.name, self.start, self.end) 


class SubTask(Task):
    """
    inherit from Task object and override the status property and the save function.
    """


    def _status(self):
        """
        returns the status of the task based on the start and end times
        of the taks and it's subtasks.
        there are three statuses defined for each task:
        a- Scheduled if the start timestamp is in future.
        b- Running if the current time is between start time and end 
           time.
        c- Complete if the end time has passed.
        """

        return Task().get_status(start_date=self.start, end_date=self.end)
            

    status = property(_status)
    
    parent_task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        null=False,
        db_index=True,
        related_name='sub_task',
        help_text="the parent task of this sub task",
    )
    

    class Meta:
        ordering = (('id'),)
        verbose_name_plural = "SubTask"


    def __str__(self):
        """
        representation of the taks object.
        """

        return "task %s " % (self.id) 


    def save(self, *args, **kwargs):
        """
        override the save function to update the start and end date of
        the parent task. the start datetime of the parent should always
        be before than the subtask start datetime. If not, update it.
        the end datetime of the parent task is equal to the highest
        end datetime of the subtask.    
        """

        try:
            ''' if save the sub task is successfull, update the start and end date of the parent_task '''
            models.Model.save(self, *args, **kwargs)

            logger.debug("saving subtask with id: {} for parent_task id: {}".format(self.id, self.parent_task.id))

            # get min and max start and end date of sub tasks
            min_startdate = SubTask.objects.filter(parent_task__id= self.parent_task.id).aggregate(Min('start'))
            max_enddate = SubTask.objects.filter(parent_task__id= self.parent_task.id).aggregate(Max('end'))
            
            logger.debug("start date min value: {} and current start value is {}".format(min_startdate['start__min'], self.parent_task.start))
            logger.debug("end date min value: {} and current end value is {}".format(max_enddate['end__max'], self.parent_task.end))

            self.parent_task.start = min_startdate['start__min']
            self.parent_task.end = max_enddate['end__max']
            self.parent_task.save(update_fields=['start', 'end'])

            logger.debug("parent task start is updated")

        except Exception as e:
            logger.error("error saving")
