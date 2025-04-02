from django.shortcuts import render, redirect
from .models import LeaveRequest
from .forms import LeaveRequestForm
from django.contrib.auth.decorators import login_required



@login_required
def leave_request_view(request):
    is_teacher = request.user.groups.filter(name__iexact='Teacher').exists()

    # Select the correct base template
    base_template = 'teacher/teacherbase.html' if is_teacher else 'student/studentbase.html'

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()
            return redirect('view_leave_requests')
    else:
        form = LeaveRequestForm(user=request.user)

    return render(request, 'leave_request.html', {
        'form': form,
        'base_template': base_template  # Pass the base template to the context
    })






@login_required
def view_leave_requests(request):
    is_teacher = request.user.groups.filter(name__iexact='Teacher').exists()

    # Select the correct base template
    if request.user.is_staff:
        base_template = 'admin/adminbase.html'  # Admin base
        leaves = LeaveRequest.objects.all()  # Admin can view all requests
    else:
        base_template = 'teacher/teacherbase.html' if is_teacher else 'student/studentbase.html'
        leaves = LeaveRequest.objects.filter(user=request.user)  # Students/Teachers view their own requests

    return render(request, 'view_leaves.html', {
        'leaves': leaves,
        'base_template': base_template  # Pass the base template to the context
    })

@login_required
def manage_leave_status(request, leave_id, action):
    if request.user.is_staff:
        leave = LeaveRequest.objects.get(id=leave_id)
        if action == 'approve':
            leave.status = 'Approved'
        elif action == 'reject':
            leave.status = 'Rejected'
        leave.save()
    return redirect('view_leave_requests')




@login_required
def leave(request):
    # Determine if the user is a teacher
    is_teacher = request.user.groups.filter(name__iexact='Teacher').exists()

    # Determine the appropriate base template
    if request.user.is_staff:
        base_template = 'admin/adminbase.html'  # Admin base
    elif is_teacher:
        base_template = 'teacher/teacherbase.html'  # Teacher base
    else:
        base_template = 'student/studentbase.html'  # Student base

    leaves = LeaveRequest.objects.filter(user=request.user) if not request.user.is_staff else LeaveRequest.objects.all()

    return render(request, 'leave.html', {
        'leaves': leaves,
        'base_template': base_template  # Pass the base template to the context
    })



