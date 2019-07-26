from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('alltasks/', views.TasksListView.as_view(), name='tasks'),
    url(r'^task/(?P<pk>[0-9]+)/$', views.TaskDetailsView.as_view(), name=views.TaskDetailsView.name),
]
