from django.http import Http404
from rest_framework.response import Response
from rest_framework import generics

from hashids import Hashids

from webgrab_main.settings import HASHIDS_SALT
from .models import TaskDetails
from .serializers import TaskDetailsSerializer
from .tasks import url_check_task
import logging


HASHIDS = Hashids(salt=HASHIDS_SALT)
log = logging.getLogger(__name__)


class TaskList(generics.ListAPIView):
    queryset = TaskDetails.objects.all()
    serializer_class = TaskDetailsSerializer
    lookup_url_kwarg = 'request_code'

    def get_queryset(self):
        request_code = self.kwargs.get('request_code')
        try:
            pks = HASHIDS.decode(request_code)
            return self.queryset.filter(pk__in=pks)
        except (AttributeError, TaskDetails.DoesNotExist):
            raise Http404


class TaskCreate(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        tasks = []
        for url in request.data.get('urls', []):
            task_details, _ = TaskDetails.objects.get_or_create(address=url)
            url_check_task.apply_async([task_details.pk])
            tasks.append(task_details.pk)
        request_code = HASHIDS.encode(*tasks)
        return Response({'request_code': request_code})
