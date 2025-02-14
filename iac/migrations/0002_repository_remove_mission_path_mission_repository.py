# Generated by Django 4.0.6 on 2022-07-09 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iac', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('remark', models.CharField(max_length=512, null=True)),
                ('content', models.FileField(upload_to='playbooks')),
            ],
        ),
        migrations.RemoveField(
            model_name='mission',
            name='path',
        ),
        migrations.AddField(
            model_name='mission',
            name='repository',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='iac.repository'),
        ),
    ]
