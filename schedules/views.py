from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Schedule
from .serializers import ScheduleSerializer
from .utils import (
    filter_by_completion_status,
    filter_by_date_range,
    filter_by_teacher,
    get_current_teacher,
    teacher_permission_required,
)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

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

        try:
            created_schedule = Schedule.create_schedule(
                teacher_id, student_id, subject_id, scheduled_at
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"status": "Schedule created", "date": created_schedule},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="create-repeating")
    def create_repeating(self, request):
        teacher_id = int(request.data.get("teacher_id"))
        student_id = int(request.data.get("student_id"))
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        frequency = int(request.data.get("frequency"))

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

    def get_queryset(self):
        teacher_id = self.request.query_params.get("teacher_id")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        is_complete = self.request.query_params.get("is_complete")

        queryset = Schedule.objects.select_related("teacher", "student", "subject")

        if teacher_id:
            queryset = filter_by_teacher(queryset, teacher_id)
        if date_from or date_to:
            queryset = filter_by_date_range(queryset, date_from, date_to)
        if is_complete is not None:
            queryset = filter_by_completion_status(queryset, is_complete)

        return queryset

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

    @teacher_permission_required
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        schedule = self.get_object()

        try:
            schedule.mark_as_complete()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Schedule marked as complete"})

    @teacher_permission_required
    def destroy(self, request, *args, **kwargs):
        schedule = self.get_object()

        try:
            schedule.delete_schedule()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
