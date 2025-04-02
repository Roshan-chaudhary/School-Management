from django.contrib import admin

# Register your models here.
from leave_management.models import LeaveRequest

admin.site.register(LeaveRequest)
