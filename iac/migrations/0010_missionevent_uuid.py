# Generated by Django 4.0.6 on 2022-07-24 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iac', '0009_missionevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='missionevent',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
    ]
