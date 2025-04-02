from django.urls import path
from . import views
from .views import edit_admin, delete_admin
urlpatterns = [
    path('', views.adminregister, name='adminregister'),
    path('admin_register_list', views.admin_register_list, name='admin_register_list'),

    path('admin/edit/<int:admin_id>/', edit_admin, name='edit_admin'),
    path('admin/delete/<int:admin_id>/', delete_admin, name='delete_admin'),
    
]
