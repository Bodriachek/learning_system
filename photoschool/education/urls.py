from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'education'

router = routers.SimpleRouter()


router.register('program', views.ProgramViewSet, basename='program-crud'),
router.register('theme', views.ThemeViewSet, basename='theme-crud'),
router.register(r'lesson/(?P<program_id>\d+)', views.LessonViewSet, basename='lesson-crud'),
# Student
router.register('student', views.StudentViewSet, basename='student-crud'),
router.register('student-access', views.StudentAccessViewSet, basename='student-crud'),

router.register('studying', views.StudyingViewSet, basename='studying'),


urlpatterns = [
    path('', include(router.urls)),
    # Program
    path('program-approve/<int:pk>/', views.ProgramApproveAPIView.as_view()),
    path('program-history/<int:pk>/', views.ProgramHistoryRollBackAPIView.as_view()),
    # Theme
    path('theme-approve/<int:pk>/', views.ThemeApproveAPIView.as_view()),
    path('theme-history/<int:pk>/', views.ThemeHistoryRollBackAPIView.as_view()),
    # Lesson
    path('lesson-approve/<int:pk>/', views.LessonApproveAPIView.as_view()),
    path('lesson-history/<int:pk>/', views.LessonHistoryRollBackAPIView.as_view()),
    path('lessons/<str:program_title>/', views.ProgramLessonsAPIView.as_view()),
    path('lessons-theme/<str:program_title>/', views.LessonsThemeAPIView.as_view()),
]

