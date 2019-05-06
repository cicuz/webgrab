from django.urls import path

from .views import TaskList, TaskCreate


# API Url patterns
urlpatterns = [
    path('', TaskCreate.as_view(), name='task-create'),
    path('<str:request_code>/', TaskList.as_view(), name='task-list')
]
