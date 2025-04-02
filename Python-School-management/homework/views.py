from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm
from school.models import StudentExtra
@login_required
def teacher_dashboard(request):
    assignments = Assignment.objects.filter(teacher=request.user)
    return render(request, 'teacher_dashboard.html', {'assignments': assignments})

@login_required
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm()
    return render(request, 'create_assignment.html', {'form': form})

@login_required
def student_dashboard(request):
    student_extra = StudentExtra.objects.get(user=request.user)  # Student ki class nikalne ke liye
    assignments = Assignment.objects.filter(class_assigned=student_extra.cl)  # Sirf usi class ke assignments fetch karo
    student_submissions = Submission.objects.filter(student=request.user)
    
    submissions_dict = {submission.assignment.id: submission for submission in student_submissions}

    return render(request, 'student_dashboard.html', {
        'assignments': assignments,
        'submissions': submissions_dict
    })



# @login_required
# def submit_homework(request, assignment_id):
#     assignment = get_object_or_404(Assignment, id=assignment_id)
#     if request.method == 'POST':
#         form = SubmissionForm(request.POST, request.FILES)
#         if form.is_valid():
#             submission = form.save(commit=False)
#             submission.assignment = assignment
#             submission.student = request.user
#             submission.status = 'submitted'
#             submission.save()
#             return redirect('student_dashboard')
#     else:
#         form = SubmissionForm()
#     return render(request, 'submit_homework.html', {'form': form, 'assignment': assignment})


@login_required
def submit_homework(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.status = 'submitted'  # Status update
            submission.save()
            return redirect('student_dashboard')  # Resubmit ka option na ho

    else:
        form = SubmissionForm()

    return render(request, 'submit_homework.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
def review_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    print("Submission Found:", submission)  # Debugging ke liye

    if request.method == 'POST':
        submission.teacher_feedback = request.POST.get('feedback')
        submission.grade = request.POST.get('grade')
        submission.status = 'reviewed'
        submission.save()
        return redirect('teacher_dashboard')

    return render(request, 'review_submission.html', {'submission': submission})
