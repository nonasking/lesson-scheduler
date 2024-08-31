from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ScheduleViewSet, StudentViewSet, TeacherViewSet

router = DefaultRouter()
router.register(r"teachers", TeacherViewSet)
router.register(r"students", StudentViewSet)
router.register(r"schedules", ScheduleViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
