from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
import random
import string
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from school.models import TeacherExtra, EmailVerification  # Import model
from school import forms  # Import forms
from school.models import StudentExtra
from django.core.mail import send_mail
from django.utils.html import format_html



def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/index.html')



#for showing signup/login button for teacher
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'admin/adminclick.html')


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')



# Logout view Admin
def logout_view(request):
    logout(request)  # Logs out the current user
    return HttpResponseRedirect('/')  # Redirect to the home page after logout



# Logout View Student
@require_POST
def custom_logout(request):
    logout(request)
    return HttpResponseRedirect('/') # Replace 'login' with your login route name







def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request,'admin/adminsignup.html',{'form':form})


def student_signup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    
    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        
        if User.objects.filter(email=form1.data['email']).exists():
            messages.error(request, 'This email is already registered. Please log in.')
            return redirect('studentsignup')  

        if form1.is_valid() and form2.is_valid():
           
            request.session['user_data'] = {
                'username': form1.cleaned_data['username'],
                'email': form1.cleaned_data['email'],
                'password': form1.cleaned_data['password'],
                'first_name': form1.cleaned_data['first_name'],  
                'last_name': form1.cleaned_data['last_name'],  
            }
            request.session['extra_data'] = form2.cleaned_data
            request.session['user_type'] = 'STUDENT'

            verification_code = ''.join(random.choices(string.digits, k=6))
            request.session['verification_code'] = verification_code

            send_verification_email(form1.cleaned_data['email'], verification_code)

            messages.success(request, 'A verification code has been sent to your email.')
            return redirect('verify_email')  

    return render(request, 'student/studentsignup.html', {'form1': form1, 'form2': form2})


def teacher_signup_view(request):
    form1 = forms.TeacherUserForm()
    form2 = forms.TeacherExtraForm()
    
    if request.method == 'POST':
        form1 = forms.TeacherUserForm(request.POST)
        form2 = forms.TeacherExtraForm(request.POST)
        
        if User.objects.filter(email=form1.data['email']).exists():
            messages.error(request, 'This email is already registered. Please log in.')
            return redirect('teachersignup') 

        if form1.is_valid() and form2.is_valid():
            
            request.session['user_data'] = {
                'username': form1.cleaned_data['username'],
                'email': form1.cleaned_data['email'],
                'password': form1.cleaned_data['password'],
                'first_name': form1.cleaned_data['first_name'],  
                'last_name': form1.cleaned_data['last_name'],  
            }
            request.session['extra_data'] = form2.cleaned_data
            request.session['user_type'] = 'TEACHER'

      
            verification_code = ''.join(random.choices(string.digits, k=6))
            request.session['verification_code'] = verification_code

            send_verification_email(form1.cleaned_data['email'], verification_code)

            messages.success(request, 'A verification code has been sent to your email.')
            return redirect('verify_email')  

    return render(request, 'teacher/teachersignup.html', {'form1': form1, 'form2': form2})


#for checking user is techer , student or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()



def afterlogin_view(request):
    if request.user.is_authenticated:
        print("Authenticated User:", request.user.username)
        print("Is Superuser:", request.user.is_superuser)
        print("Groups:", request.user.groups.all())

        if request.user.is_superuser:
            return redirect('admin-dashboard')
        elif is_teacher(request.user):
            accountapproval = models.TeacherExtra.objects.filter(user_id=request.user.id, status=True)
            if accountapproval.exists():
                return redirect('teacher-dashboard')
            else:
                return render(request, 'teacher/teacher_wait_for_approval.html')
        elif is_student(request.user):
            accountapproval = models.StudentExtra.objects.filter(user_id=request.user.id, status=True)
            if accountapproval.exists():
                return redirect('student-dashboard')
            else:
                return render(request, 'student/student_wait_for_approval.html')
    return redirect('adminlogin')




#for dashboard of adminnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    teachercount=models.TeacherExtra.objects.all().filter(status=True).count()
    pendingteachercount=models.TeacherExtra.objects.all().filter(status=False).count()

    studentcount=models.StudentExtra.objects.all().filter(status=True).count()
    pendingstudentcount=models.StudentExtra.objects.all().filter(status=False).count()

    teachersalary=models.TeacherExtra.objects.filter(status=True).aggregate(Sum('salary'))
    pendingteachersalary=models.TeacherExtra.objects.filter(status=False).aggregate(Sum('salary'))

    studentfee=models.StudentExtra.objects.filter(status=True).aggregate(Sum('fee',default=0))
    pendingstudentfee=models.StudentExtra.objects.filter(status=False).aggregate(Sum('fee'))

    notice=models.Notice.objects.all()

    #aggregate function return dictionary so fetch data from dictionay
    mydict={
        'teachercount':teachercount,
        'pendingteachercount':pendingteachercount,

        'studentcount':studentcount,
        'pendingstudentcount':pendingstudentcount,

        'teachersalary':teachersalary['salary__sum'],
        'pendingteachersalary':pendingteachersalary['salary__sum'],

        'studentfee':studentfee['fee__sum'],
        'pendingstudentfee':pendingstudentfee['fee__sum'],

        'notice':notice

    }

    return render(request,'admin/admin_dashboard.html',context=mydict)







#for teacher sectionnnnnnnn by adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_teacher_view(request):
    return render(request,'admin/admin_teacher.html')

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_add_teacher_view(request):
    form1=forms.TeacherUserForm()
    form2=forms.TeacherExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.TeacherUserForm(request.POST)
        form2=forms.TeacherExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()

            f2=form2.save(commit=False)
            f2.user=user
            f2.status=True
            f2.save()

            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-teacher')
    return render(request,'admin/admin_add_teacher.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_view_teacher_view(request):
    teachers = models.TeacherExtra.objects.all().filter(status=True)  # Only approved teachers
    return render(request, 'admin/admin_view_teacher.html', {'teachers': teachers})



@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_approve_teacher_view(request):
    teachers=models.TeacherExtra.objects.all().filter(status=False)
    return render(request,'admin/admin_approve_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def approve_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    teacher.status=True
    teacher.save()
    return redirect(reverse('admin-approve-teacher'))


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def delete_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-approve-teacher')


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def delete_teacher_from_school_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-view-teacher')



@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def update_teacher_view(request, pk):
    teacher = get_object_or_404(models.TeacherExtra, id=pk)
    user = get_object_or_404(models.User, id=teacher.user_id)

    # Save the current password & email to preserve them
    current_password = user.password
    current_email = user.email
    current_status = teacher.status

    if request.method == 'POST':
        form1 = forms.TeacherUserForm(request.POST, instance=user)
        form2 = forms.TeacherExtraForm(request.POST, instance=teacher)

        if form1.is_valid() and form2.is_valid():
            user_instance = form1.save(commit=False)

            # **Preserve the current email and password, and hash the password**
            user_instance.email = current_email
            user_instance.password = current_password  # Ensure it's the hashed password

            # **Save only fields you want to update, excluding email and password**
            user_instance.save(update_fields=['first_name', 'last_name', 'username'])

            # **Save teacher data, preserving the status**
            teacher_instance = form2.save(commit=False)
            teacher_instance.status = current_status  # Preserve the current status
            teacher_instance.save(update_fields=['salary', 'mobile', 'status'])

            # Redirect to the teacher list (approved teachers)
            return redirect('admin-view-teacher')

    else:
        form1 = forms.TeacherUserForm(instance=user)
        form2 = forms.TeacherExtraForm(instance=teacher)

    mydict = {'form1': form1, 'form2': form2}
    return render(request, 'admin/admin_update_teacher.html', context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_view_teacher_salary_view(request):
    teachers=models.TeacherExtra.objects.all()
    return render(request,'admin/admin_view_teacher_salary.html',{'teachers':teachers})






#for student by adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_student_view(request):
    return render(request,'admin/admin_student.html')


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_add_student_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            print("form is valid")
            user=form1.save()
            user.set_password(user.password)
            user.save()

            f2=form2.save(commit=False)
            f2.user=user
            f2.status=True
            f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        else:
            print("form is invalid")
        return HttpResponseRedirect('admin-student')
    return render(request,'admin/admin_add_student.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_view_student_view(request):
    students=models.StudentExtra.objects.all().filter(status=True)
    return render(request,'admin/admin_view_student.html',{'students':students})


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def delete_student_from_school_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-view-student')


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def delete_student_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-approve-student')

from django.contrib.auth.hashers import make_password  # Import this for hashing

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def update_student_view(request, pk):
    student = models.StudentExtra.objects.get(id=pk)
    user = models.User.objects.get(id=student.user_id)

    # Form ko initialize karna
    form1 = forms.StudentUserForm(instance=user)
    form2 = forms.StudentExtraForm(instance=student)

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST, instance=user)
        form2 = forms.StudentExtraForm(request.POST, instance=student)

        if form1.is_valid() and form2.is_valid():
            print("✅ Forms are valid!")

            user_instance = form1.save(commit=False)

            # ❌ Email change nahi karni
            user_instance.email = user.email  

            # ❌ Password change nahi karni
            user_instance.password = user.password  

            user_instance.save()

            # ✅ Student extra form update ho
            student_instance = form2.save(commit=False)
            student_instance.status = True
            student_instance.save()

            print("✅ Student updated successfully!")

            return redirect('admin-view-student')

        else:
            print("❌ Form Errors:", form1.errors, form2.errors)

    mydict = {'form1': form1, 'form2': form2}
    return render(request, 'admin/admin_update_student.html', context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_approve_student_view(request):
    students=models.StudentExtra.objects.all().filter(status=False)
    return render(request,'admin/admin_approve_student.html',{'students':students})


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def approve_student_view(request,pk):
    students=models.StudentExtra.objects.get(id=pk)
    students.status=True
    students.save()
    return redirect(reverse('admin-approve-student'))


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_view_student_fee_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'admin/admin_view_student_fee.html',{'students':students})






#attendance related viewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_attendance_view(request):
    return render(request,'admin/admin_attendance.html')


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_take_attendance_view(request,cl):
    students=models.StudentExtra.objects.all().filter(cl=cl)
    print(students)
    aform=forms.AttendanceForm()
    if request.method=='POST':
        form=forms.AttendanceForm(request.POST)
        if form.is_valid():
            Attendances=request.POST.getlist('present_status')
            date=form.cleaned_data['date']
            for i in range(len(Attendances)):
                AttendanceModel=models.Attendance()
                AttendanceModel.cl=cl
                AttendanceModel.date=date
                AttendanceModel.present_status=Attendances[i]
                AttendanceModel.roll=students[i].roll
                AttendanceModel.save()
            return redirect('admin-attendance')
        else:
            print('form invalid')
    return render(request,'admin/admin_take_attendance.html',{'students':students,'aform':aform})



@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_view_attendance_view(request,cl):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            attendancedata=models.Attendance.objects.all().filter(date=date,cl=cl)
            studentdata=models.StudentExtra.objects.all().filter(cl=cl)
            mylist=zip(attendancedata,studentdata)
            return render(request,'admin/admin_view_attendance_page.html',{'cl':cl,'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'admin/admin_view_attendance_ask_date.html',{'cl':cl,'form':form})









#fee related view by adminnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_fee_view(request):
    return render(request,'admin/admin_fee.html')


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_view_fee_view(request,cl):
    feedetails=models.StudentExtra.objects.all().filter(cl=cl)
    return render(request,'admin/admin_view_fee.html',{'feedetails':feedetails,'cl':cl})








#notice related viewsssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_notice_view(request):
    form=forms.NoticeForm()
    if request.method=='POST':
        form=forms.NoticeForm(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            form.by=request.user.first_name
            form.save()
            return redirect('admin-dashboard')
    return render(request,'admin/admin_notice.html',{'form':form})








#for TEACHER  LOGIN    SECTIONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    teacherdata=models.TeacherExtra.objects.all().filter(status=True,user_id=request.user.id)
    notice=models.Notice.objects.all()
    mydict={
        'salary':teacherdata[0].salary,
        'mobile':teacherdata[0].mobile,
        'date':teacherdata[0].joindate,
        'notice':notice
    }
    return render(request,'teacher/teacher_dashboard.html',context=mydict)



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_attendance_view(request):
    return render(request,'teacher/teacher_attendance.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_take_attendance_view(request,cl):
    students=models.StudentExtra.objects.all().filter(cl=cl)
    aform=forms.AttendanceForm()
    if request.method=='POST':
        form=forms.AttendanceForm(request.POST)
        if form.is_valid():
            Attendances=request.POST.getlist('present_status')
            date=form.cleaned_data['date']
            for i in range(len(Attendances)):
                AttendanceModel=models.Attendance()
                AttendanceModel.cl=cl
                AttendanceModel.date=date
                AttendanceModel.present_status=Attendances[i]
                AttendanceModel.roll=students[i].roll
                AttendanceModel.save()
            return redirect('teacher-attendance')
        else:
            print('form invalid')
    return render(request,'teacher/teacher_take_attendance.html',{'students':students,'aform':aform})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_attendance_view(request,cl):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            attendancedata=models.Attendance.objects.all().filter(date=date,cl=cl)
            studentdata=models.StudentExtra.objects.all().filter(cl=cl)
            mylist=zip(attendancedata,studentdata)
            return render(request,'teacher/teacher_view_attendance_page.html',{'cl':cl,'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'teacher/teacher_view_attendance_ask_date.html',{'cl':cl,'form':form})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_notice_view(request):
    form=forms.NoticeForm()
    if request.method=='POST':
        form=forms.NoticeForm(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            form.by=request.user.first_name
            form.save()
            return redirect('teacher-dashboard')
        else:
            print('form invalid')
    return render(request,'teacher/teacher_notice.html',{'form':form})







#FOR STUDENT AFTER THEIR Loginnnnnnnnnnnnnnnnnn
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    studentdata=models.StudentExtra.objects.all().filter(status=True,user_id=request.user.id)
    notice=models.Notice.objects.all()
    mydict={
        'roll':studentdata[0].roll,
        'mobile':studentdata[0].mobile,
        'fee':studentdata[0].fee,
        'notice':notice
    }
    return render(request,'student/student_dashboard.html',context=mydict)



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_attendance_view(request):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            studentdata=models.StudentExtra.objects.all().filter(user_id=request.user.id,status=True)
            attendancedata=models.Attendance.objects.all().filter(date=date,cl=studentdata[0].cl,roll=studentdata[0].roll)
            mylist=zip(attendancedata,studentdata)
            return render(request,'student/student_view_attendance_page.html',{'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'student/student_view_attendance_ask_date.html',{'form':form})









# for aboutus and contact ussssssssssssssssssssssssssssssssssssssssssssss
def aboutus_view(request):
    return render(request,'school/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'school/contactussuccess.html')
    return render(request, 'school/contactus.html', {'form':sub})






from django.shortcuts import get_object_or_404



def verify_email(request):
    if request.method == "POST":
        code_entered = request.POST['code']
        stored_code = request.session.get('verification_code')
        
        if stored_code and code_entered == stored_code:
            user_data = request.session.get('user_data')
            extra_data = request.session.get('extra_data')
            user_type = request.session.get('user_type')
            
            if user_data and extra_data:
                # ✅ Ab database me save karna
                user = User.objects.create_user(
                    username=user_data['username'],
                    first_name=user_data['first_name'],  
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    password=user_data['password']
                )
                user.save()
                
                # Save Extra Data
                if user_type == 'STUDENT':
                    StudentExtra.objects.create(user=user, **extra_data)
                    group, _ = Group.objects.get_or_create(name='STUDENT')
                else:
                    TeacherExtra.objects.create(user=user, **extra_data)
                    group, _ = Group.objects.get_or_create(name='TEACHER')
                
                group.user_set.add(user)

                # Clean up session data
                del request.session['user_data']
                del request.session['extra_data']
                del request.session['verification_code']

                return render(request, "verification_success.html") 
            else:
                messages.error(request, "Session expired. Please sign up again.")
                return redirect('student_signup' if user_type == 'STUDENT' else 'teacher_signup')

        else:
            messages.error(request, "Invalid verification code. Try again.")

    return render(request, "verify_email.html")


def send_verification_email(email, verification_code):
    subject = "🔒 Verify Your Email - Action Required"
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 500px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333;">🔐 Email Verification</h2>
                <p style="font-size: 16px; color: #555;">
                    Hello, <br><br>
                    Thank you for signing up! Please use the verification code below to activate your account:
                </p>
                <div style="font-size: 20px; font-weight: bold; padding: 10px; background: #007bff; color: white; text-align: center; border-radius: 6px;">
                    {verification_code}
                </div>
                <p style="font-size: 14px; color: #777;">This code is valid for a limited time.</p>
                <p style="font-size: 14px; color: #777;">
                    If you did not request this, please ignore this email.
                </p>
                <br>
                <p style="font-size: 12px; color: #aaa;">Best Regards, <br><strong>Your Website Team</strong></p>
            </div>
        </body>
    </html>
    """

    send_mail(
        subject,
        "",  
        "example@dommain.com",  
        [email],
        fail_silently=False,
        html_message=html_message, 
    )

from school.models import UserProfile

from django.http import JsonResponse

def save_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        try:
            
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            
            profile_picture = request.FILES['profile_picture']
            user_profile.profile_picture = profile_picture
            user_profile.save()

            
            profile_picture_url = user_profile.profile_picture.url
            return JsonResponse({"success": True, "image_url": profile_picture_url})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})