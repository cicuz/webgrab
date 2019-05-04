import hashlib
import os
import requests
from django.core.files import File
from django.utils import timezone
from tempfile import NamedTemporaryFile

from webgrab_main.celery import app
from selenium import webdriver
from .models import TaskDetails

import logging


log = logging.getLogger('celery')
SELENIUM_DRIVER_URL = os.environ.get("SELENIUM_DRIVER_URL")


@app.task(ignore_result=True)
def url_check_task(taskdetails_pk=None):
    if taskdetails_pk is not None:
        task_details = TaskDetails.objects.get(pk=taskdetails_pk)
    else:
        task_details, created = TaskDetails.objects.get_or_create(address='https://www.ilpost.it')
    task_details.started = True
    try:
        response = requests.head(task_details.address)
        task_details.status_code = response.status_code
        if response.status_code == requests.codes.ok:
            # execute screengrab task only if HTTP status code is 200
            url_grab_task.apply_async([task_details.pk])
    except requests.exceptions.RequestException as e:
        log.error(e)
        task_details.error = f'{e}'
    # avoid overwriting fields in case the next task has already started
    task_details.save(update_fields=['started', 'status_code', 'error'])
    log.debug(task_details)


@app.task(ignore_result=True)
def url_grab_task(taskdetails_pk):
    def md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    task_details = TaskDetails.objects.get(pk=taskdetails_pk)
    driver = webdriver.Remote(SELENIUM_DRIVER_URL, webdriver.DesiredCapabilities.CHROME)
    driver.get(task_details.address)
    temp_file = NamedTemporaryFile(suffix='.png')
    driver.save_screenshot(temp_file.name)
    hash = md5(temp_file.name)
    task_details.image_file.save(f"{hash[:2]}/{hash}.png", File(temp_file), save=False)
    task_details.image_download_datetime = timezone.now()
    driver.quit()
    task_details.completed = True
    task_details.save(update_fields=['completed', 'image_file', 'image_download_datetime'])
    log.debug(task_details)
