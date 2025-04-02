from django.urls import path
from . import views

urlpatterns = [
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/create/', views.create_assignment, name='create_assignment'),

    
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/submit/<int:assignment_id>/', views.submit_homework, name='submit_homework'),
    path('teacher/review/<int:submission_id>/', views.review_submission, name='review_submission'),
]
