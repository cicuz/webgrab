from rest_framework import serializers

from .models import TaskDetails


class TaskDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskDetails
        fields = ['address', 'started', 'completed', 'status_code', 'error',
                  'image_file', 'image_download_datetime']
