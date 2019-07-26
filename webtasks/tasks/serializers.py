from rest_framework import serializers
from .models import Task


class TaskDetailSerializer(serializers.ModelSerializer):
    """ 
    a simple serializer used by the api with three readonly fields,
    the priority and the owner's first and lastname only.
    """

    task_priority = serializers.ReadOnlyField(source='priority')
    first_name = serializers.ReadOnlyField(source='owner.first_name')
    last_name = serializers.ReadOnlyField(source='owner.last_name')

    class Meta:
        model = Task
        fields = ('task_priority', 'first_name', 'last_name')
