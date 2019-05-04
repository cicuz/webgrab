from django.conf.urls import url
from django.urls import include

from .views import TaskList, TaskCreate


# API Url patterns
urlpatterns = [
    url(r'', include([
            url(r'^$', TaskCreate.as_view(), name="task-create"),
            url(r'^(?P<request_code>.+)/$', TaskList.as_view(), name="task-list")
    ])),
]
