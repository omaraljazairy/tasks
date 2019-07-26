from django.shortcuts import render
from django.http import HttpResponse
from .models import Task
from .serializers import TaskDetailSerializer
from django.views import generic
from rest_framework import generics, status
import logging

logger = logging.getLogger('tasks')

def index(request):
    """ 
    render the index page which can contain any info needed. In this 
    case I added a summary of the tasks stored to the context to be
    rendered in the index.html page.
    """

    logger.debug("index view started")
    total_tasks = Task.objects.count()
    total_subtasks = Task.objects.filter(parent_task__isnull=True).count()
    tasks = Task.objects.all()
    task_status = [task.status for task in tasks]
    total_status = {k:task_status.count(k) for k in task_status}
    task_durations = sorted([task.duration for task in tasks])
    
    context = {
        'total_tasks' : total_tasks,
        'total_subtasks': total_subtasks,
        'total_status': total_status,
        'durations': task_durations,
    }

    return render(request, 'index.html', context=context)


class TaskDetailsView(generics.RetrieveAPIView):
    """ 
    use the RetrieveAPIView to allow only the get request. it will
    use a custom serializer to get only the values needed.
    """

    logger.debug("view request")
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer

    name = 'task-details'


class TasksListView(generic.ListView):
    """ 
    using the generics ListView which supports only GET requests.
    list all the tasks. 
    """

    model = Task
    context_object_name = 'tasks_list'
    queryset = Task.objects.all()
    template_name = 'tasks.html'

