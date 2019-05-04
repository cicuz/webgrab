from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class IndexedTimeStampedModel(models.Model):
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)

    class Meta:
        abstract = True


class TaskDetails(IndexedTimeStampedModel):
    address = models.URLField(unique=True)
    started = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    status_code = models.IntegerField(null=True)
    error = models.CharField(max_length=1024, null=True)
    image_file = models.ImageField(upload_to='screenshots', null=True)
    image_download_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.address} started: {self.started} completed: {self.completed} status_Code: {self.status_code} error: {self.error}'
