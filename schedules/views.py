from rest_framework import viewsets, status
from .models import Teacher, Student, Schedule
from .serializers import TeacherSerializer, StudentSerializer, ScheduleSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from datetime import timedelta

def get_current_teacher(request):
    teacher_id = request.headers.get('Teacher-ID')
    if not teacher_id:
        raise ValidationError({'error': 'Teacher-ID header is required.'})
    
    try:
        return Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValidationError({'error': 'Invalid Teacher-ID.'})
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        queryset = Schedule.objects.all()

        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from and date_to:
            queryset = queryset.filter(scheduled_at__range=[date_from, date_to])
        elif date_from:
            queryset = queryset.filter(scheduled_at__gte=date_from)
        elif date_to:
            queryset = queryset.filter(scheduled_at__lte=date_to)
        
        is_complete = self.request.query_params.get('is_complete')
        if is_complete is not None:
            queryset = queryset.filter(is_complete=is_complete.lower() == 'true')

        return queryset

    def create(self, request, *args, **kwargs):
        teacher_id = request.data.get('teacher_id')
        student_id = request.data.get('student_id')
        scheduled_at = request.data.get('scheduled_at')

        current_teacher_id = get_current_teacher(request).id
        if current_teacher_id != teacher_id:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if Schedule.objects.filter(teacher_id=teacher_id, student_id=student_id, scheduled_at=scheduled_at).exists():
            return Response({'error': 'Schedule already exists for the given teacher, student, and date.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        schedule = self.get_object()

        current_teacher = get_current_teacher(request)
        if current_teacher != schedule.teacher:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if schedule.is_complete:
            return Response({'error': 'Completed schedules cannot be deleted.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        current_teacher = get_current_teacher(request)
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)

        schedules = Schedule.objects.filter(
            teacher=current_teacher,
            scheduled_at__year=year,
            scheduled_at__month=month,
        ).values('scheduled_at').annotate(count=Count('id')).order_by('scheduled_at')

        return Response({schedule['scheduled_at'].strftime('%Y-%m-%d'): schedule['count'] for schedule in schedules})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        schedule = self.get_object()
        
        current_teacher = get_current_teacher(request)
        if current_teacher != schedule.teacher:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if schedule.is_complete:
            return Response({'error': 'Schedule is already completed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        schedule.is_complete = True
        schedule.completed_date = timezone.now().date()
        schedule.save()
        return Response({'status': 'Schedule marked as complete'})
    
    @action(detail=False, methods=['post'])
    def create_repeating(self, request):
        teacher_id = request.data.get('teacher_id')
        student_id = request.data.get('student_id')
        subject_id = request.data.get('student_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        frequency = request.data.get('frequency', 2)

        current_teacher_id = get_current_teacher(request).id
        if current_teacher_id != teacher_id:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            start_date = timezone.make_aware(timezone.datetime.fromisoformat(start_date))
            end_date = timezone.make_aware(timezone.datetime.fromisoformat(end_date))
        except ValueError:
            return Response({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)

        if end_date > timezone.now() + timedelta(days=365):
            return Response({'error': 'End date cannot be more than 1 year from today.'}, status=status.HTTP_400_BAD_REQUEST)

        if frequency in [2, 4]:
            delta = timedelta(weeks=frequency)
        else:
            return Response({'error': 'Invalid frequency. Choose either 2 or 4 weeks.'}, status=status.HTTP_400_BAD_REQUEST)

        current_date = start_date
        created_schedules = []
        while current_date <= end_date:
            if not Schedule.objects.filter(
                teacher_id=teacher_id,
                student_id=student_id,
                scheduled_at=current_date.date()
            ).exists():
                Schedule.objects.create(
                    teacher_id=teacher_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    scheduled_at=current_date.date()
                )
                created_schedules.append(current_date.date())
            current_date += delta

        return Response({'status': 'Schedules created', 'dates': created_schedules}, status=status.HTTP_201_CREATED)