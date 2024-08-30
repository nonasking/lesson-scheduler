import re
from rest_framework import viewsets, status
from .models import Teacher, Student, Schedule
from .serializers import TeacherSerializer, StudentSerializer, ScheduleSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        teacher_id = request.data.get('teacher_id')
        student_id = request.data.get('student_id')
        scheduled_at = request.data.get('scheduled_at')

        if Schedule.objects.filter(teacher_id=teacher_id, student_id=student_id, scheduled_at=scheduled_at).exists():
            return Response({'error': 'Schedule already exists for the given teacher, student, and date.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)

        schedules = Schedule.objects.filter(
            scheduled_at__year=year,
            scheduled_at__month=month,
        ).values('scheduled_at').annotate(count=Count('id')).order_by('scheduled_at')

        return Response({schedule['scheduled_at'].strftime('%Y-%m-%d'): schedule['count'] for schedule in schedules})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        schedule = self.get_object()
        
        if not (request.data['teacher_id'] == schedule.teacher.id):
            return Response({'error': 'You do not have permission to complete this schedule.'}, status=status.HTTP_403_FORBIDDEN)

        if schedule.is_complete:
            return Response({'error': 'Schedule is already completed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        schedule.is_complete = True
        schedule.completed_date = timezone.now().date()
        schedule.save()
        return Response({'status': 'Schedule marked as complete'})
    
    def destroy(self, request, *args, **kwargs):
        schedule = self.get_object()
        if schedule.is_complete:
            return Response({'error': 'Completed schedules cannot be deleted.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)