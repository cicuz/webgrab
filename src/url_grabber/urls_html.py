from django.urls import path

from .views import TaskHTMLListView, TaskHTMLFormView


# HTML Url patterns
urlpatterns = [
    path('', TaskHTMLFormView.as_view(), name='task-create-html'),
    path('<str:request_code>/', TaskHTMLListView.as_view(http_method_names=['get',]), name='task-list-html')
]
