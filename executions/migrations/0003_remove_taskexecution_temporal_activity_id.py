# Generated by Django 5.2 on 2025-04-22 03:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("executions", "0002_remove_taskexecution_next_retry_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="taskexecution",
            name="temporal_activity_id",
        ),
    ]
