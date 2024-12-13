from django.db import models
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask


class TimestampMixIn(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditMixin(TimestampMixIn):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name="+")
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name="+")

    class Meta:
        abstract = True


class Repository(AuditMixin, models.Model):
    name = models.CharField(max_length=32)
    remark = models.CharField(max_length=512, null=True)
    url = models.CharField(max_length=512, null=True)


class MissionState(models.IntegerChoices):
    PENDING = 0, 'PENDING'
    RUNNING = 1, 'RUNNING'
    COMPLETED = 2, 'COMPLETED'
    FAILED = 3, 'FAILED'
    CANCELED = 4, 'CANCELED'
    TIMEOUT = 5, 'TIMEOUT'
    CANCELING = 6, 'CANCELING'


class MissionMode(models.IntegerChoices):
    MANUAL = 0, 'MANUAL'
    PERIODIC = 1, 'PERIODIC'


class MissionTemplate(AuditMixin, models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.PROTECT)
    playbook = models.CharField(max_length=64)
    inventories = models.TextField(null=True)

    class Meta:
        abstract = True


class Mission(MissionTemplate):
    mode = models.IntegerField(default=MissionMode.MANUAL)
    state = models.IntegerField(choices=MissionState.choices, default=MissionState.PENDING)
    output = models.TextField(null=True)
    commit = models.CharField(max_length=40, null=True)

    class Meta:
        ordering = ["-created_at"]


class MissionEvent(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="events")
    state = models.CharField(max_length=60)
    uuid = models.UUIDField()
    host = models.CharField(max_length=128)
    play = models.CharField(max_length=128)
    play_pattern = models.CharField(max_length=128)
    task = models.CharField(max_length=128)
    task_action = models.CharField(max_length=128)
    task_args = models.TextField()
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    duration = models.FloatField(null=True)
    res = models.JSONField(null=True)
    changed = models.BooleanField(default=False)


class PeriodicMission(MissionTemplate):
    scheduler = models.OneToOneField(PeriodicTask, on_delete=models.PROTECT, null=True, related_name="periodic_mission")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.save_base(False, force_insert, force_update, using, update_fields)
        self.scheduler.args = f"[{self.id}]"
        self.scheduler.periodic_mission = self
        self.scheduler.save()
        super(PeriodicMission, self).save(force_update=True)


class Authorization(TimestampMixIn, models.Model):
    token = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expired_at = models.DateTimeField(null=False)

    class Meta:
        index_together = [["token", "expired_at"]]
