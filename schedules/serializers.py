from rest_framework import serializers
from .models import Teacher, Student, Schedule

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'user_name', 'human_name', 'subject']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user_name', 'human_name']

class ScheduleSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'teacher', 'student', 'subject', 'is_complete', 'completed_date', 'scheduled_at', 'created_at', 'modified_at']

    def create(self, validated_data):
        # 유효성 검사 및 수업 생성 로직 구현
        schedule = Schedule.objects.create(**validated_data)
        return schedule
