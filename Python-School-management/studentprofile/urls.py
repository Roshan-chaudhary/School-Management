from django.urls import path
from studentprofile import views

urlpatterns = [
    path('profile/', views.student_profile_view, name='student_profile'),
]
