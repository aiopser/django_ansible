import os
import uuid

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codebox.settings')
django.setup()

from iac.models import PeriodicMission
from django_celery_beat.models import PeriodicTask, IntervalSchedule

if __name__ == '__main__':
    interval = IntervalSchedule.objects.create(every=1, period='minutes')
    scheduler = PeriodicTask()
    scheduler.interval = interval
    scheduler.name = uuid.uuid4().hex
    scheduler.task = 'iac.tasks.submit'
    PeriodicMission.objects.create(
        repository_id=1,
        playbook='playbook.yaml',
        scheduler=scheduler
    )
