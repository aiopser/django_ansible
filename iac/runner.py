import threading
import pathlib
from datetime import datetime

from git import Repo
from django.conf import settings
from django.utils import timezone
from ansible_runner.interface import run
from .models import Mission, MissionState, MissionEvent


class Runner:
    def __init__(self, model: Mission):
        self.model = model
        self.workdir = pathlib.Path(settings.IAC_WORKDIR, str(self.model.id))

    def prepare(self):
        self.workdir.mkdir(parents=True)
        repo = Repo.clone_from(self.model.repository.url, self.workdir)
        if self.model.inventories:
            with open(self.workdir.joinpath("inventory/hosts"), 'w') as writer:
                writer.write(self.model.inventories)
        self.model.commit = repo.head.commit.hexsha

    def on_event(self, event):
        if event["event"].startswith("runner_on"):
            uuid = event["parent_uuid"]
            data = event["event_data"]
            host = data['host']
            try:
                model = MissionEvent.objects.filter(uuid=uuid, host=host).get()
            except MissionEvent.DoesNotExist:
                model = MissionEvent()
            model.uuid = uuid
            model.mission = self.model
            model.state = event["event"].removeprefix("runner_on_")
            model.play = data["play"]
            model.play_pattern = data["play_pattern"]
            model.task = data["task"]
            model.task_action = data["task_action"]
            model.task_args = data["task_args"]
            model.host = host
            model.res = data.get("res", {})
            dt = data.get("start")
            if dt:
                model.start = timezone.make_aware(datetime.fromisoformat(dt))
            dt = data.get("end")
            if dt:
                model.end = timezone.make_aware(datetime.fromisoformat(dt))
            model.duration = data.get("duration")
            model.changed = data.get("res", {}).get("changed", False)
            model.save()

    def on_status(self, status: dict, runner_config):
        if status == "starting":
            self.model.state = MissionState.RUNNING
        if status == "running":
            self.model.state = MissionState.RUNNING
        if status == "canceled":
            self.model.state = MissionState.CANCELED
        if status == "timeout":
            self.model.state = MissionState.TIMEOUT
        if status == "failed":
            self.model.state = MissionState.FAILED
        if status == "successful":
            self.model.state = MissionState.COMPLETED
        # match status['status']:
        #     case "starting" | "running":
        #         self.model.state = MissionState.RUNNING
        #     case "canceled":
        #         self.model.state = MissionState.CANCELED
        #     case "timeout":
        #         self.model.state = MissionState.TIMEOUT
        #     case "failed":
        #         self.model.state = MissionState.FAILED
        #     case "successful":
        #         self.model.state = MissionState.COMPLETED
        # self.model.save()

    def on_finished(self, *args, **kwargs):
        pass

    @classmethod
    def cancel(cls, mission: Mission):
        if mission.state == MissionState.RUNNING or mission.state == MissionState.PENDING:
            mission.state = MissionState.CANCELING
            mission.save()

    def is_canceled(self):
        return Mission.objects.get(id=self.model.id).state == MissionState.CANCELING

    def exec(self):
        try:
            self.prepare()
            runner = run(private_data_dir=self.workdir,
                         playbook=self.model.playbook,
                         event_handler=self.on_event,
                         cancel_callback=self.is_canceled,
                         status_handler=self.on_status,
                         finished_callback=self.on_finished)
            self.model.output = runner.stdout.read()
        except Exception as e:
            self.model.state = MissionState.FAILED
        finally:
            self.model.save()
