from django.urls import path
from teacherprofile import views  # Import your views

urlpatterns = [
    path('profile/', views.teacher_profile_view, name='teacher_profile'),
]
