from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_required
def student_profile_view(request):
    student = request.user  

    if request.method == 'POST':
        if 'update_profile' in request.POST: 
            new_username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            if User.objects.exclude(id=student.id).filter(username=new_username).exists():
                messages.error(request, 'Username already taken! Please choose another.')
            else:
                student.username = new_username
                student.first_name = first_name
                student.last_name = last_name
                student.save()

                messages.success(request, 'Profile updated successfully!')
                return redirect('student_profile')

        elif 'change_password' in request.POST:  
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                student.set_password(new_password)
                student.save()

                update_session_auth_hash(request, student)
                messages.success(request, 'Password changed successfully!')
                return redirect('student_profile')
            else:
                messages.error(request, 'Passwords do not match!')

    return render(request, 'studentprofile.html', {'student': student})
