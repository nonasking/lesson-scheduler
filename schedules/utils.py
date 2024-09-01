from functools import wraps

from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Teacher


# 유저 확인 함수
def get_current_teacher(request):
    teacher_id = request.headers.get("Teacher-ID")
    if not teacher_id:
        raise ValidationError({"error": "Teacher-ID header is required."})

    try:
        return Teacher.objects.select_related("subject").get(id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValidationError({"error": "Invalid Teacher-ID."})


def teacher_permission_required(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        current_teacher = get_current_teacher(request)
        schedule = self.get_object()

        if schedule.teacher != current_teacher:
            raise PermissionDenied({"error": "Permission denied"})

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view


# 데이터 가공 함수
def filter_by_teacher(queryset, teacher_id):
    queryset = queryset.filter(teacher_id=teacher_id)
    return queryset


def filter_by_date_range(queryset, date_from=None, date_to=None):
    if date_from and date_to:
        if date_from > date_to:
            raise ValidationError("Date_from cannot be later then date_to.")
        queryset = queryset.filter(scheduled_at__range=[date_from, date_to])
    elif date_from:
        queryset = queryset.filter(scheduled_at__gte=date_from)
    elif date_to:
        queryset = queryset.filter(scheduled_at__lte=date_to)
    return queryset


def filter_by_completion_status(queryset, is_complete):
    queryset = queryset.filter(is_complete=is_complete.lower() == "true")
    return queryset
