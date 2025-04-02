from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('submitted', 'Submitted'),
    ('reviewed', 'Reviewed'),
]

classes = [
    ('one', 'one'), ('two', 'two'), ('three', 'three'),
    ('four', 'four'), ('five', 'five'), ('six', 'six'),
    ('seven', 'seven'), ('eight', 'eight'), ('nine', 'nine'), ('ten', 'ten')
]

class Assignment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    class_assigned = models.CharField(max_length=10, choices=classes, default='one')  # <-- Class field add kiya

    def __str__(self):
        return f"{self.title} ({self.class_assigned})"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    attachment = models.FileField(upload_to='submissions/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    teacher_feedback = models.TextField(blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
