# Generated by Django 4.0.6 on 2022-07-24 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iac', '0011_alter_missionevent_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='missionevent',
            name='changed',
            field=models.BooleanField(default=False),
        ),
    ]
