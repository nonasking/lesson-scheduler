
# 데이터 가공 함수
def filter_by_teacher(queryset, teacher_id):
    queryset = queryset.filter(teacher_id=teacher_id)
    return queryset

def filter_by_date_range(queryset, date_from=None, date_to=None):
    if date_from and date_to:
        queryset = queryset.filter(scheduled_at__range=[date_from, date_to])
    elif date_from:
        queryset = queryset.filter(scheduled_at__gte=date_from)
    elif date_to:
        queryset = queryset.filter(scheduled_at__lte=date_to)
    return queryset

def filter_by_completion_status(queryset, is_complete):
    queryset = queryset.filter(is_complete=is_complete.lower() == "true")
    return queryset