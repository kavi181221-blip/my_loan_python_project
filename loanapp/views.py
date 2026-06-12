from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import UserProfile, LoanApplication, Payment


import random
import string


def send_loan_email(loan, subject, template_name):
    """Send email notification about loan application"""
    try:
        context = {
            'loan': loan,
            'user': loan.user,
            'user_profile': loan.user.userprofile,
        }

        html_message = render_to_string(f'emails/{template_name}.html', context)
        plain_message = render_to_string(f'emails/{template_name}.txt', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[loan.applicant_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def home(request):
    # Always show home page with register/login buttons
    # Don't redirect logged-in users - let them see the home page too
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone = request.POST['phone']
        address = request.POST['address']
        income = request.POST['income']
        employment = request.POST['employment']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(
            user=user,
            phone=phone,
            address=address,
            monthly_income=income,
            employment_type=employment
        )
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials!')
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    loans = LoanApplication.objects.filter(user=request.user)
    total_loans = loans.count()
    active_loans = loans.filter(status__in=['Approved', 'Disbursed']).count()
    total_borrowed = loans.filter(status__in=['Approved', 'Disbursed', 'Completed']).aggregate(Sum('amount'))['amount__sum'] or 0
    pending_amount = loans.filter(status__in=['Approved', 'Disbursed']).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'loans': loans[:5],
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_borrowed': total_borrowed,
        'pending_amount': pending_amount
    }
    return render(request, 'dashboard.html', context)

@login_required
def apply_loan(request):
    if request.method == 'POST':
        loan_type = request.POST['loan_type']
        # Convert strings to appropriate types!
        amount = float(request.POST['amount'])           # Convert to float
        tenure = int(request.POST['tenure'])           # Convert to int!
        purpose = request.POST['purpose']
        applicant_email = request.POST['email']

        loan = LoanApplication.objects.create(
            user=request.user,
            loan_type=loan_type,
            amount=amount,          # Now it's a Decimal/float
            tenure_months=tenure,   # Now it's an integer!
            purpose=purpose,
            applicant_email=applicant_email,
            interest_rate=10.5 if loan_type == 'Personal' else 8.5 if loan_type == 'Home' else 9.0
        )
        loan.calculate_emi()
        
        # Send confirmation email
        send_loan_email(loan, 'Loan Application Submitted', 'loan_submitted')
        
        messages.success(request, 'Loan application submitted successfully!')

        return redirect('loan_status')

    return render(request, 'apply_loan.html')

@login_required
def loan_status(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-applied_date')
    return render(request, 'loan_status.html', {'loans': loans})

@login_required
def loan_details(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)
    payments = Payment.objects.filter(loan=loan)
    return render(request, 'loan_details.html', {'loan': loan, 'payments': payments})

@login_required
def make_payment(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id, user=request.user)

    if request.method == 'POST':
        amount = request.POST['amount']
        method = request.POST['method']
        trans_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        Payment.objects.create(
            loan=loan,
            amount_paid=amount,
            payment_method=method,
            transaction_id=trans_id
        )
        messages.success(request, 'Payment successful!')

        return redirect('loan_details', loan_id=loan.id)

    return render(request, 'payment.html', {'loan': loan})

@login_required
def calculator(request):
    emi_result = None
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        rate = float(request.POST['rate'])
        tenure = int(request.POST['tenure'])

        r = rate / (12 * 100)
        emi = amount * r * (1 + r)**tenure / ((1 + r)**tenure - 1)
        total = emi * tenure

        emi_result = {
            'emi': round(emi, 2),
            'total': round(total, 2),
            'interest': round(total - amount, 2)
        }

    return render(request, 'calculator.html', {'emi_result': emi_result})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()

        profile.phone = request.POST['phone']
        profile.address = request.POST['address']
        profile.save()
        messages.success(request, 'Profile updated successfully!')

    return render(request, 'profile.html', {'profile': profile})

# Admin Views
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    total_applications = LoanApplication.objects.count()
    pending_count = LoanApplication.objects.filter(status='Pending').count()
    approved_amount = LoanApplication.objects.filter(status='Disbursed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_users = User.objects.filter(is_staff=False).count()

    recent_loans = LoanApplication.objects.select_related('user').order_by('-applied_date')[:10]

    context = {
        'total_applications': total_applications,
        'pending_count': pending_count,
        'approved_amount': approved_amount,
        'total_users': total_users,
        'recent_loans': recent_loans
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def manage_loans(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    status = request.GET.get('status', 'all')
    if status == 'all':
        loans = LoanApplication.objects.select_related('user').order_by('-applied_date')
    else:
        loans = LoanApplication.objects.filter(status=status).select_related('user').order_by('-applied_date')

    return render(request, 'manage_loans.html', {'loans': loans, 'filter': status})

@login_required
def update_loan_status(request, loan_id):
    if not request.user.is_staff:
        return redirect('dashboard')

    loan = get_object_or_404(LoanApplication, id=loan_id)
    if request.method == 'POST':
        new_status = request.POST['status']
        loan.status = new_status
        if new_status == 'Approved':
            loan.approved_date = timezone.now()
            loan.approved_by = request.user
        loan.save()
        messages.success(request, f'Loan status updated to {new_status}')
    return redirect('manage_loans')