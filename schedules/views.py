from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Schedule, Student, Teacher
from .serializers import ScheduleSerializer, StudentSerializer, TeacherSerializer


def get_current_teacher(request):
    teacher_id = request.headers.get("Teacher-ID")
    if not teacher_id:
        raise ValidationError({"error": "Teacher-ID header is required."})

    try:
        return Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValidationError({"error": "Invalid Teacher-ID."})


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

        queryset = self.filter_by_teacher(queryset)
        queryset = self.filter_by_date_range(queryset)
        queryset = self.filter_by_completion_status(queryset)

        return queryset

    def filter_by_teacher(self, queryset):
        teacher_id = self.request.query_params.get("teacher_id")
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        return queryset

    def filter_by_date_range(self, queryset):
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from and date_to:
            queryset = queryset.filter(scheduled_at__range=[date_from, date_to])
        elif date_from:
            queryset = queryset.filter(scheduled_at__gte=date_from)
        elif date_to:
            queryset = queryset.filter(scheduled_at__lte=date_to)
        return queryset

    def filter_by_completion_status(self, queryset):
        is_complete = self.request.query_params.get("is_complete")
        if is_complete is not None:
            queryset = queryset.filter(is_complete=is_complete.lower() == "true")
        return queryset

    def create(self, request, *args, **kwargs):
        teacher_id = int(request.data.get("teacher_id"))
        student_id = int(request.data.get("student_id"))
        scheduled_at = request.data.get("scheduled_at")

        current_teacher = get_current_teacher(request)
        current_teacher_id = current_teacher.id
        subject_id = current_teacher.subject.id
        if current_teacher_id != teacher_id:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        if Schedule.objects.filter(
            teacher_id=teacher_id, student_id=student_id, scheduled_at=scheduled_at
        ).exists():
            return Response(
                {"error": "This schedule already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data._mutable = True
        request.data.update({"subject_id": subject_id})
        request.data._mutable = False

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        schedule = self.get_object()

        current_teacher = get_current_teacher(request)
        if current_teacher != schedule.teacher:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            schedule.delete_schedule()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        current_teacher = get_current_teacher(request)
        year = request.query_params.get("year", timezone.now().year)
        month = request.query_params.get("month", timezone.now().month)

        schedules = (
            Schedule.objects.filter(
                teacher=current_teacher,
                scheduled_at__year=year,
                scheduled_at__month=month,
            )
            .values("scheduled_at")
            .annotate(count=Count("id"))
            .order_by("scheduled_at")
        )

        return Response(
            {
                schedule["scheduled_at"].strftime("%Y-%m-%d"): schedule["count"]
                for schedule in schedules
            }
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        schedule = self.get_object()

        current_teacher = get_current_teacher(request)
        if current_teacher != schedule.teacher:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            schedule.mark_as_complete()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Schedule marked as complete"})

    @action(detail=False, methods=["post"], url_path="create-repeating")
    def create_repeating(self, request):
        teacher_id = int(request.data.get("teacher_id"))
        student_id = int(request.data.get("student_id"))
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        frequency = int(request.data.get("frequency", 2))

        current_teacher = get_current_teacher(request)
        current_teacher_id = current_teacher.id
        subject_id = current_teacher.subject.id
        if current_teacher_id != teacher_id:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            created_schedules = Schedule.create_repeating_schedules(
                teacher_id, student_id, subject_id, start_date, end_date, frequency
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"status": "Schedules created", "dates": created_schedules},
            status=status.HTTP_201_CREATED,
        )
