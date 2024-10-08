# Generated by Django 4.2.15 on 2024-08-31 13:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("schedules", "0002_alter_teacher_subject"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="subject",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
