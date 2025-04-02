from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_required
def teacher_profile_view(request):
    teacher = request.user  # Current logged-in teacher

    if request.method == 'POST':
        if 'update_profile' in request.POST:  # Profile Update
            new_username = request.POST.get('username')  # Get new username
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            # Check if username already exists
            if User.objects.exclude(id=teacher.id).filter(username=new_username).exists():
                messages.error(request, 'Username already taken! Please choose another.')
            else:
                teacher.username = new_username  # Update username
                teacher.first_name = first_name
                teacher.last_name = last_name
                teacher.save()

                messages.success(request, 'Profile updated successfully!')
                return redirect('teacher_profile')

        elif 'change_password' in request.POST:  # Password Change
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                teacher.set_password(new_password)
                teacher.save()

                update_session_auth_hash(request, teacher)  # Keep the user logged in
                messages.success(request, 'Password changed successfully!')
                return redirect('teacher_profile')
            else:
                messages.error(request, 'Passwords do not match!')

    return render(request, 'teacherprofile.html', {'teacher': teacher})
