# Generated by Django 4.0.6 on 2022-07-24 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iac', '0013_alter_mission_state_alter_missionevent_mission_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='mode',
            field=models.IntegerField(default=0),
        ),
    ]
