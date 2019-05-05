from django.conf.urls import url

from .views import TaskList, TaskCreate


# API Url patterns
urlpatterns = [
    url(r'^$', TaskCreate.as_view(), name='task-create'),
    url(r'^(?P<request_code>.+)/$', TaskList.as_view(), name='task-list')
]
