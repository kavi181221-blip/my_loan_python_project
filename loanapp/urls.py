from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/', views.apply_loan, name='apply_loan'),
    path('status/', views.loan_status, name='loan_status'),
    path('loan/<int:loan_id>/', views.loan_details, name='loan_details'),
    path('payment/<int:loan_id>/', views.make_payment, name='make_payment'),
    path('calculator/', views.calculator, name='calculator'),
    path('profile/', views.profile, name='profile'),
    

    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/loans/', views.manage_loans, name='manage_loans'),
    path('admin/loan/<int:loan_id>/update/', views.update_loan_status, name='update_loan'),
]