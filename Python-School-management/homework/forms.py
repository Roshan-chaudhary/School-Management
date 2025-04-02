from django import forms
from .models import Assignment, Submission

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'attachment', 'class_assigned']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['attachment']
