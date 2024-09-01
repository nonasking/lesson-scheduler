from rest_framework import serializers

from .models import Schedule, Student, Subject, Teacher


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ["id", "user_name", "human_name", "subject"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "korean_name", "english_name"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "user_name", "human_name"]


class ScheduleSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()
    student = StudentSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = Schedule
        fields = [
            "id",
            "teacher",
            "student",
            "subject",
            "is_complete",
            "completed_date",
            "scheduled_at",
            "created_at",
            "modified_at",
        ]
