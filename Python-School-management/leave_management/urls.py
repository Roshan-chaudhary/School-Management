from django.contrib import admin
from django.urls import path,include
from leave_management import views
from django.contrib.auth.views import LoginView,LogoutView

urlpatterns = [
    path('leave-request/', views.leave_request_view, name='leave_request'),
    path('view-leave-requests/', views.view_leave_requests, name='view_leave_requests'),
    path('manage-leave/<int:leave_id>/<str:action>/', views.manage_leave_status, name='manage_leave'),


    path('',views.leave,name='leave'),


]