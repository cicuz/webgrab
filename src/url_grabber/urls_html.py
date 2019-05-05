from django.conf.urls import url

from .views import TaskHTMLListView, TaskHTMLFormView


# HTML Url patterns
urlpatterns = [
    url(r'^$', TaskHTMLFormView.as_view(), name='task-create-html'),
    url(r'^(?P<request_code>.+)/$', TaskHTMLListView.as_view(), name='task-list-html')
]
