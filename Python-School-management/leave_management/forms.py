from django import forms
from .models import LeaveRequest

# class LeaveRequestForm(forms.ModelForm):
#     class Meta:
#         model = LeaveRequest
#         fields = ['leave_type','user_type', 'start_date', 'end_date', 'reason', 'attachment']
#         widgets = {
#             'start_date': forms.DateInput(attrs={'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date'}),
#             'reason': forms.Textarea(attrs={'rows': 3}),
#         }






class LeaveRequestForm(forms.ModelForm):
    user_type = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Debugging Statements
        print(f"DEBUG: Logged in user: {user}")
        print(f"DEBUG: User is_staff: {user.is_staff}")

        if user:
            # Case-insensitive group check
            if user.groups.filter(name__iexact='Teacher').exists():
                self.fields['user_type'].initial = 'Teacher'
                print("DEBUG: Assigned as Teacher")
            else:
                self.fields['user_type'].initial = 'Student'
                print("DEBUG: Assigned as Student")

    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'user_type', 'start_date', 'end_date', 'reason', 'attachment']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
