# schedules/tests.py

from django.test import TestCase
from .models import Teacher, Student, Schedule
from django.utils import timezone

class ScheduleTestCase(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(username='teacher1', human_name='김모모', subject='Korean')
        self.student = Student.objects.create(username='student1', human_name='다래')
        self.schedule = Schedule.objects.create(teacher=self.teacher, student=self.student, subject='Korean', scheduled_at=timezone.now().date())

    def test_schedule_creation(self):
        self.assertEqual(Schedule.objects.count(), 1)

    def test_schedule_completion(self):
        self.schedule.is_complete = True
        self.schedule.completed_date = timezone.now().date()
        self.schedule.save()
        self.assertTrue(self.schedule.is_complete)

    def test_unique_schedule(self):
        with self.assertRaises(Exception):
            Schedule.objects.create(teacher=self.teacher, student=self.student, subject='Korean', scheduled_at=self.schedule.scheduled_at)
