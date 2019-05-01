import shlex
import subprocess  # nosec

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import autoreload


def restart_celery(*_, celery_type, **__):
    kill_celery_cmd = "pkill -9 celery"
    subprocess.call(shlex.split(kill_celery_cmd))  # nosec
    start_celery_cmd = f"celery -A webgrab_main {celery_type} -l info"
    subprocess.call(shlex.split(start_celery_cmd))  # nosec


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("celery_type", type=str, choices=["beat", "worker"])

    def handle(self, *args, celery_type, **options):  # pylint: disable=arguments-differ
        if not settings.DEBUG:
            raise CommandError("This command can only be ran when DEBUG is True")
        self.stdout.write(f"Starting celery {celery_type} with autoreload...")
        autoreload.run_with_reloader(restart_celery, **{"celery_type": celery_type})
