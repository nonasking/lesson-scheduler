from datetime import timedelta

from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .constants import FREQUENCY_CHOICES


class User(models.Model):
    user_name = models.CharField(max_length=255, unique=True)
    human_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Subject(models.Model):
    korean_name = models.CharField(max_length=100, unique=True)
    english_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Teacher(User):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)


class Student(User):
    pass


class Schedule(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    scheduled_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_schedule(cls, teacher_id, student_id, subject_id, scheduled_at):
        if Schedule.objects.filter(
            teacher_id=teacher_id, student_id=student_id, scheduled_at=scheduled_at
        ).exists():
            raise ValidationError("This schedule already exists.")

        Schedule.objects.create(
            teacher_id=teacher_id,
            student_id=student_id,
            subject_id=subject_id,
            scheduled_at=scheduled_at,
        )
        return scheduled_at

    @classmethod
    def create_repeating_schedules(
        cls, teacher_id, student_id, subject_id, start_date, end_date, frequency
    ):
        try:
            start_date = timezone.make_aware(
                timezone.datetime.fromisoformat(start_date)
            )
            end_date = timezone.make_aware(timezone.datetime.fromisoformat(end_date))
        except ValueError:
            raise ValidationError("Invalid date format. Use ISO format (YYYY-MM-DD).")

        if start_date > end_date:
            raise ValidationError("Start date cannot be later then end date.")

        if end_date > timezone.now() + timedelta(days=365):
            raise ValidationError("End date cannot be more than 1 year from today.")

        existing_schedules = Schedule.objects.filter(
            teacher_id=teacher_id,
            student_id=student_id,
            scheduled_at__range=[start_date, end_date],
        ).values_list("scheduled_at", flat=True)

        if frequency in FREQUENCY_CHOICES:
            delta = timedelta(weeks=frequency)
        else:
            raise ValidationError("Invalid frequency. Choose either 2 or 4 weeks.")

        current_date = start_date

        schedules_to_create = []
        created_schedules = []
        while current_date <= end_date:
            if current_date.date() not in existing_schedules:
                schedules_to_create.append(
                    Schedule(
                        teacher_id=teacher_id,
                        student_id=student_id,
                        subject_id=subject_id,
                        scheduled_at=current_date.date(),
                        created_at=timezone.now(),
                        modified_at=timezone.now(),
                    )
                )
                created_schedules.append(current_date.date())
            current_date += delta

        if schedules_to_create:
            Schedule.objects.bulk_create(schedules_to_create)

        return created_schedules

    def mark_as_complete(self):
        if self.is_complete:
            raise ValidationError("Schedule is already completed.")
        self.is_complete = True
        self.completed_date = timezone.now().date()
        self.save()

    def delete_schedule(self):
        if self.is_complete:
            raise ValidationError("Completed schedules cannot be deleted.")
        self.delete()

    class Meta:
        unique_together = ("teacher", "student", "scheduled_at")
