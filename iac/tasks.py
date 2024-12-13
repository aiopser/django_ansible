import time

from celery import shared_task
from .models import Mission, MissionMode
from .runner import Runner


@shared_task
def add(x, y):
    time.sleep(30)
    return x + y


@shared_task
def execute(mission_id):
    mission = Mission.objects.get(id=mission_id)
    runner = Runner(mission)
    runner.exec()


@shared_task
def submit(template_id):
    template = Mission.objects.get(id=template_id)
    mission = Mission.objects.create(
        repository=template.repository,
        playbook=template.playbook,
        inventories=template.inventories,
        mode=MissionMode.PERIODIC
    )
    execute.delay(mission.id)
