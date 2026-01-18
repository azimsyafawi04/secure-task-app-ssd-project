from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('guest/', views.guest_page, name='guest_page'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/audit-logs/', views.audit_logs_all, name='audit_logs_all'),
    path('admin-dashboard/users/', views.admin_user_management, name='admin_user_management'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path("inventory/", views.inventory_list, name="inventory_list"),
    path("inventory/add/", views.inventory_create, name="inventory_create"),
    path("inventory/edit/<int:item_id>/", views.inventory_edit, name="inventory_edit"),
    path("inventory/delete/<int:item_id>/", views.inventory_delete, name="inventory_delete"),
    path('admin-dashboard/users/edit-password/<int:user_id>/', views.admin_user_edit_password, name='admin_user_edit_password'),
    path('admin-dashboard/users/delete/<int:user_id>/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-dashboard/users/edit-departments/<int:user_id>/', views.admin_user_edit_departments, name='admin_user_edit_departments'),
    path('admin-dashboard/users/reactivate/<int:user_id>/', views.admin_user_reactivate, name='admin_user_reactivate'),
    
    # Department URLs
    path('admin-dashboard/departments/', views.department_list, name='department_list'),
    path('admin-dashboard/departments/add/', views.department_create, name='department_create'),
    path('admin-dashboard/departments/edit/<int:dept_id>/', views.department_edit, name='department_edit'),
    path('admin-dashboard/departments/delete/<int:dept_id>/', views.department_delete, name='department_delete'),
]