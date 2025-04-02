from django.db import models
from django.contrib.auth.models import User

LEAVE_TYPES = [
    ('Sick Leave', 'Sick Leave'),
    ('Casual Leave', 'Casual Leave'),
    ('Personal Leave', 'Personal Leave'),
]

LEAVE_STATUS = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
]

USER_TYPES = [
    ('Student', 'Student'),
    ('Teacher', 'Teacher'),
]

class LeaveRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField(default=0)
    reason = models.TextField()
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='Pending')

    def save(self, *args, **kwargs):
        self.total_days = (self.end_date - self.start_date).days + 1

        if self.user.groups.filter(name='Student').exists():
            self.user_type = 'Student'
        elif self.user.groups.filter(name='Teacher').exists():
            self.user_type = 'Teacher'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.user_type}) - {self.leave_type} - {self.status}"
