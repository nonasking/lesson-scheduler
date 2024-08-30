from rest_framework import serializers
from .models import Teacher, Student, Schedule, Subject

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'user_name', 'human_name', 'subject']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'korean_name', 'english_name']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user_name', 'human_name']

class ScheduleSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        source='teacher',
        write_only=True
    )
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        write_only=True
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source='subject',
        write_only=True
    )

    class Meta:
        model = Schedule
        fields = ['id', 'teacher', 'student', 'subject', 'is_complete', 'completed_date', 'scheduled_at', 'created_at', 'modified_at', 'teacher_id', 'student_id', 'subject_id']
