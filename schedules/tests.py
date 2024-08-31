from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Schedule, Student, Subject, Teacher


class ScheduleViewSetTest(APITestCase):

    def setUp(self):
        self.subject = Subject.objects.create(korean_name="수학", english_name="Math")
        self.teacher = Teacher.objects.create(
            user_name="teacher1",
            human_name="John Doe",
            password="password123",
            subject=self.subject,
        )
        self.student = Student.objects.create(
            user_name="student1", human_name="Jane Doe", password="password123"
        )
        self.schedule_url = reverse("schedule-list")

        self.client.credentials(HTTP_TEACHER_ID=self.teacher.id)

    def test_create_schedule(self):
        data = {
            "teacher_id": self.teacher.id,
            "student_id": self.student.id,
            "subject_id": self.subject.id,
            "scheduled_at": (timezone.now() + timedelta(days=7)).date(),
        }
        response = self.client.post(self.schedule_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)

    def test_create_repeating_schedule(self):
        schedule = Schedule.objects.create(
            teacher=self.teacher,
            student=self.student,
            subject=self.subject,
            scheduled_at=(timezone.now() + timedelta(days=7)).date(),
        )
        data = {
            "teacher_id": self.teacher.id,
            "student_id": self.student.id,
            "subject_id": self.subject.id,
            "scheduled_at": schedule.scheduled_at,
        }
        response = self.client.post(self.schedule_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Schedule.objects.count(), 1)

    def test_create_schedule_without_permission(self):
        another_teacher = Teacher.objects.create(
            user_name="teacher2",
            human_name="Alice",
            password="password123",
            subject=self.subject,
        )
        data = {
            "teacher_id": another_teacher.id,
            "student_id": self.student.id,
            "subject_id": self.subject.id,
            "scheduled_at": (timezone.now() + timedelta(days=7)).date(),
        }
        response = self.client.post(self.schedule_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Schedule.objects.count(), 0)

    def test_delete_schedule(self):
        schedule = Schedule.objects.create(
            teacher=self.teacher,
            student=self.student,
            subject=self.subject,
            scheduled_at=(timezone.now() + timedelta(days=7)).date(),
        )
        url = reverse("schedule-detail", kwargs={"pk": schedule.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Schedule.objects.count(), 0)

    def test_delete_completed_schedule(self):
        schedule = Schedule.objects.create(
            teacher=self.teacher,
            student=self.student,
            subject=self.subject,
            scheduled_at=(timezone.now() + timedelta(days=7)).date(),
            is_complete=True,
            completed_date=timezone.now().date(),
        )
        url = reverse("schedule-detail", kwargs={"pk": schedule.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Schedule.objects.count(), 1)

    def test_dashboard_view(self):
        Schedule.objects.create(
            teacher=self.teacher,
            student=self.student,
            subject=self.subject,
            scheduled_at=timezone.now().date(),
        )
        url = reverse("schedule-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(timezone.now().strftime("%Y-%m-%d"), response.data)
        self.assertEqual(response.data[timezone.now().strftime("%Y-%m-%d")], 1)

    def test_complete_schedule(self):
        schedule = Schedule.objects.create(
            teacher=self.teacher,
            student=self.student,
            subject=self.subject,
            scheduled_at=(timezone.now() + timedelta(days=7)).date(),
        )
        url = reverse("schedule-complete", kwargs={"pk": schedule.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        schedule.refresh_from_db()
        self.assertTrue(schedule.is_complete)
        self.assertIsNotNone(schedule.completed_date)

    def test_create_repeating_schedule(self):
        data = {
            "teacher_id": self.teacher.id,
            "student_id": self.student.id,
            "subject_id": self.subject.id,
            "start_date": timezone.now().date().isoformat(),
            "end_date": (timezone.now() + timedelta(weeks=8)).date().isoformat(),
            "frequency": 2,
        }
        url = reverse("schedule-create-repeating")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["dates"]), 5)
        self.assertEqual(Schedule.objects.count(), 5)
