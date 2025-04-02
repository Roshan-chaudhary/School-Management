from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import AdminSignupForm
from django.contrib.auth.models import User  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages



def adminregister(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('admin_register_list')
    else:
        form = AdminSignupForm()
    
    return render(request, 'admin_register.html', {'form': form})




def admin_register_list(request):
    admins = User.objects.filter(is_staff=True)  
    return render(request, 'admin_register_list.html', {'admins': admins, 'admincount': admins.count()})









@login_required
def edit_admin(request, admin_id):
    admin = get_object_or_404(User, id=admin_id)
    
    if request.method == "POST":
        admin.username = request.POST.get("username", admin.username)
        admin.first_name = request.POST.get("first_name", admin.first_name)
        admin.last_name = request.POST.get("last_name", admin.last_name)
        admin.email = request.POST.get("email", admin.email)

        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password and confirm_password:
            if new_password == confirm_password:
                admin.set_password(new_password)
            else:
                messages.error(request, "Passwords do not match")
                return render(request, "edit_admin.html", {"admin": admin})

        admin.save()
        messages.success(request, "Admin details updated successfully!")
        return redirect("admin_register_list")  

    return render(request, "edit_admin.html", {"admin": admin})

@login_required
def delete_admin(request, admin_id):
    admin = get_object_or_404(User, id=admin_id)
    
    if request.user == admin:
        messages.error(request, "You cannot delete yourself.")
        return redirect("admin_register_list")
    
    admin.delete()
    messages.success(request, "Admin deleted successfully!")
    return redirect("admin_register_list")