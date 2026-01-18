from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import InventoryItem, AuditLog, Department, UserProfile
from .forms import InventoryItemForm

def get_client_ip(request):
    # Vulnerability Fix: Use REMOTE_ADDR instead of X-Forwarded-For to prevent IP spoofing 
    # unless a trusted proxy is explicitly configured to sanitize the header.
    return request.META.get('REMOTE_ADDR')

def log_audit(user, action, resource, resource_id=None, details="", ip=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip
    )

def home(request):
    return render(request, "core/home.html")

def guest_page(request):
    return render(request, "core/home.html") # Alias for home if needed

from django.db.models import Q

@login_required
def dashboard_redirect(request):
    if request.user.is_staff:
        # Clear notification when admin visits dashboard if desired, 
        # but the requirement says "after admin views user list".
        return redirect('admin_dashboard')
    return redirect('user_dashboard')

@login_required
def user_dashboard(request):
    # Requirement: User can see items they created, assigned to them, or in their department
    user_items = InventoryItem.objects.filter(
        Q(owner=request.user) | 
        Q(assigned_to=request.user) | 
        Q(department__users__user=request.user)
    ).distinct()
    user_items_count = user_items.count()
    
    # Get user's departments
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_departments = profile.departments.all()
    
    return render(request, "core/user_dashboard.html", {
        'count': user_items_count,
        'user_departments': user_departments
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    audit_logs = AuditLog.objects.all().order_by('-timestamp')[:10]
    total_items = InventoryItem.objects.count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    
    # Check for new user notification
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    show_notification = not profile.has_seen_new_users
    
    return render(request, "core/admin_dashboard.html", {
        'audit_logs': audit_logs,
        'total_items': total_items,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'show_notification': show_notification,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def audit_logs_all(request):
    audit_logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, "core/audit_logs_all.html", {'audit_logs': audit_logs})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_user_management(request):
    users = User.objects.all().order_by('username')
    
    # Requirement: Clear notification after admin views user list
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.has_seen_new_users = True
    profile.save()
    
    return render(request, "core/admin_user_management.html", {'users': users})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_user_reactivate(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        target_user.is_active = True
        target_user.save()
        log_audit(request.user, 'UPDATE', 'User', target_user.id, f"Reactivated user: {target_user.username}", get_client_ip(request))
        messages.success(request, f"User {target_user.username} has been reactivated.")
        return redirect('admin_user_management')
    return render(request, 'core/admin_user_confirm_reactivate.html', {'target_user': target_user})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_user_edit_password(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'UPDATE', 'UserPassword', target_user.id, f"Changed password for user: {target_user.username}", get_client_ip(request))
            messages.success(request, f"Password for {target_user.username} updated successfully.")
            return redirect('admin_user_management')
    else:
        form = SetPasswordForm(target_user)
    return render(request, 'core/admin_user_edit_password.html', {'form': form, 'target_user': target_user})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_user_delete(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        target_user.is_active = False
        target_user.save()
        log_audit(request.user, 'DELETE', 'User', target_user.id, f"Deactivated user (soft delete): {target_user.username}", get_client_ip(request))
        messages.success(request, f"User {target_user.username} has been deactivated.")
        return redirect('admin_user_management')
    return render(request, 'core/admin_user_confirm_delete.html', {'target_user': target_user})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_user_edit_departments(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=target_user)
    
    if request.method == 'POST':
        dept_ids = request.POST.getlist('departments')
        profile.departments.set(dept_ids)
        log_audit(request.user, 'UPDATE', 'UserProfile_Departments', target_user.id, f"Updated departments for user: {target_user.username}", get_client_ip(request))
        messages.success(request, f"Departments for {target_user.username} updated.")
        return redirect('admin_user_management')
    
    departments = Department.objects.all()
    user_depts = profile.departments.all()
    return render(request, 'core/admin_user_edit_departments.html', {
        'target_user': target_user,
        'departments': departments,
        'user_depts': user_depts
    })

# Department Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def department_list(request):
    departments = Department.objects.all()
    return render(request, "core/department_list.html", {"departments": departments})

@login_required
@user_passes_test(lambda u: u.is_staff)
def department_create(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        dept = Department.objects.create(name=name, description=description)
        log_audit(request.user, 'CREATE', 'Department', dept.id, f"Created department: {dept.name}", get_client_ip(request))
        messages.success(request, f"Department '{dept.name}' created.")
        return redirect("department_list")
    return render(request, "core/department_form.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def department_edit(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    if request.method == "POST":
        dept.name = request.POST.get('name')
        dept.description = request.POST.get('description')
        dept.save()
        log_audit(request.user, 'UPDATE', 'Department', dept.id, f"Updated department: {dept.name}", get_client_ip(request))
        messages.success(request, f"Department '{dept.name}' updated.")
        return redirect("department_list")
    return render(request, "core/department_form.html", {"dept": dept})

@login_required
@user_passes_test(lambda u: u.is_staff)
def department_delete(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    if request.method == "POST":
        if dept.items.exists():
            messages.error(request, "Cannot delete department with items.")
        else:
            name = dept.name
            dept.delete()
            log_audit(request.user, 'DELETE', 'Department', dept_id, f"Deleted department: {name}", get_client_ip(request))
            messages.success(request, f"Department '{name}' deleted.")
        return redirect("department_list")
    return render(request, "core/department_confirm_delete.html", {"dept": dept})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_audit(user, 'CREATE', 'User', user.id, "User registered", get_client_ip(request))
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard_redirect")
    else:
        form = UserCreationForm()
    return render(request, "core/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_audit(user, 'LOGIN', 'User', user.id, "User logged in", get_client_ip(request))
            return redirect('dashboard_redirect')
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})

@login_required
def logout_view(request):
    log_audit(request.user, 'LOGOUT', 'User', request.user.id, "User logged out", get_client_ip(request))
    logout(request)
    return redirect("login")

@login_required
def inventory_list(request):
    if request.user.is_staff:
        # Admin sees ALL inventory items.
        items = InventoryItem.objects.all()
    else:
        # User sees: created by them OR assigned to them OR in their department
        items = InventoryItem.objects.filter(
            Q(owner=request.user) | 
            Q(assigned_to=request.user) | 
            Q(department__users__user=request.user)
        ).distinct()
    return render(request, "core/inventory_list.html", {"items": items})

@login_required
def inventory_create(request):
    if request.method == "POST":
        form = InventoryItemForm(request.POST, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            
            # Auto-assign department for normal users
            if not request.user.is_staff:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                if profile.departments.exists():
                    item.department = profile.departments.first()

            item.save()
            
            # Since department and assigned_to are in the form, 
            # form.save() handles them if they are in the form.
            # But commit=False means we need to save m2m if any, 
            # though here they are ForeignKeys, so item.save() is enough.
            # However, we need to ensure they are saved.
            form.save_m2m() # Just in case
            
            log_audit(request.user, 'CREATE', 'InventoryItem', item.id, f"Created item: {item.name}", get_client_ip(request))
            messages.success(request, f"Item '{item.name}' created successfully.")
            return redirect("inventory_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InventoryItemForm(user=request.user)
    
    return render(request, "core/inventory_add.html", {
        "form": form,
    })

@login_required
def inventory_edit(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    
    # Check ownership or admin status or assignment or department
    can_edit = request.user.is_staff or \
               item.owner == request.user or \
               item.assigned_to == request.user or \
               (item.department and item.department.users.filter(user=request.user).exists())
               
    if not can_edit:
        messages.error(request, "You do not have permission to edit this item.")
        return redirect("inventory_list")
        
    if request.method == "POST":
        form = InventoryItemForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            item = form.save()
            log_audit(request.user, 'UPDATE', 'InventoryItem', item.id, f"Updated item: {item.name}", get_client_ip(request))
            messages.success(request, f"Item '{item.name}' updated successfully.")
            return redirect("inventory_list")
    else:
        form = InventoryItemForm(instance=item, user=request.user)
    
    return render(request, "core/inventory_form.html", {
        "form": form, 
        "item": item,
    })

@login_required
def inventory_delete(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    
    can_delete = request.user.is_staff or \
                 item.owner == request.user
                 
    if not can_delete:
        messages.error(request, "You do not have permission to delete this item.")
        return redirect("inventory_list")

    if request.method == "POST":
        name = item.name
        item.delete()
        log_audit(request.user, 'DELETE', 'InventoryItem', item_id, f"Deleted item: {name}", get_client_ip(request))
        messages.success(request, f"Item '{name}' deleted successfully.")
        return redirect("inventory_list")
    return render(request, "core/inventory_confirm_delete.html", {"item": item})
