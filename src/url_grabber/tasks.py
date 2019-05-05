import hashlib
import os
import requests
from django.core.files import File
from django.utils import timezone
from tempfile import NamedTemporaryFile
from selenium.common.exceptions import WebDriverException

from webgrab_main.celery import app
from selenium import webdriver
from .models import TaskDetails

import datetime
import logging


log = logging.getLogger(__name__)
SELENIUM_DRIVER_URL = os.environ.get("SELENIUM_DRIVER_URL")
MIN_TIMEDELTA = datetime.timedelta(minutes=2)


@app.task(ignore_result=True)
def url_check_task(taskdetails_pk):
    task_details = TaskDetails.objects.get(pk=taskdetails_pk)
    if task_details.image_download_datetime is not None and \
            timezone.now() - task_details.image_download_datetime <= MIN_TIMEDELTA:
        log.debug(f'Not spawning url_grab_task for {task_details.address}')
        return
    task_details.started = True
    try:
        response = requests.head(task_details.address)
        task_details.status_code = response.status_code
        task_details.error = None
        if response.status_code == requests.codes.ok:
            """
            Execute screengrab task only if HTTP status code is 200.
            Mostly, this code is to lazily check we're dealing with an actual URL here
            """
            url_grab_task.apply_async([task_details.pk])
        else:
            task_details.completed = True
            task_details.save()
            log.debug(f'Not spawning url_grab_task for {task_details.address}: '
                      f'status code {response.status_code}')
            return
    except requests.exceptions.RequestException as e:
        log.error(e)
        task_details.error = f'{e}'
    # avoid overwriting fields in case the next task has already started
    task_details.save(update_fields=['started', 'status_code', 'error'])
    log.debug(task_details)


@app.task(bind=True, ignore_result=True)
def url_grab_task(self, taskdetails_pk):
    def md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    task_details = TaskDetails.objects.get(pk=taskdetails_pk)
    try:
        driver = webdriver.Remote(SELENIUM_DRIVER_URL, webdriver.DesiredCapabilities.CHROME)
        driver.get(task_details.address)
        temp_file = NamedTemporaryFile(suffix='.png')
        driver.save_screenshot(temp_file.name)
        hash = md5(temp_file.name)
        task_details.image_file.save(f"{hash[:2]}/{hash}.png", File(temp_file), save=False)
        task_details.image_download_datetime = timezone.now()
        driver.quit()
    except WebDriverException as e:
        log.error(e)
        raise self.retry(exc=e, max_retries=5)
    task_details.completed = True
    task_details.save(update_fields=['completed', 'image_file', 'image_download_datetime'])
    log.debug(task_details)
