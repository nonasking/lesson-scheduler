from django.db import models


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

    class Meta:
        unique_together = ("teacher", "student", "scheduled_at")
