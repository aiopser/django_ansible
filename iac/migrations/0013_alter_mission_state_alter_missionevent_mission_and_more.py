# Generated by Django 4.0.6 on 2022-07-24 09:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('iac', '0012_missionevent_changed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='state',
            field=models.IntegerField(choices=[(0, 'PENDING'), (1, 'RUNNING'), (2, 'COMPLETED'), (3, 'FAILED'), (4, 'CANCELED'), (5, 'TIMEOUT'), (6, 'CANCELING')], default=0),
        ),
        migrations.AlterField(
            model_name='missionevent',
            name='mission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='iac.mission'),
        ),
        migrations.CreateModel(
            name='MissionTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('playbook', models.CharField(max_length=64)),
                ('inventories', models.TextField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='iac.repository')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
