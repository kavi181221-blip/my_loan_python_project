from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    employment_type = models.CharField(max_length=50, choices=[
        ('Salaried', 'Salaried'),
        ('Self-Employed', 'Self-Employed'),
        ('Business', 'Business'),
        ('Student', 'Student')
    ])
    credit_score = models.IntegerField(default=700)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class LoanApplication(models.Model):
    LOAN_TYPES = [
        ('Personal', 'Personal Loan'),
        ('Home', 'Home Loan'),
        ('Car', 'Car Loan'),
        ('Education', 'Education Loan'),
        ('Business', 'Business Loan'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Disbursed', 'Disbursed'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_months = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.5)
    purpose = models.TextField()
    applicant_email = models.EmailField(default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')
    monthly_emi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_payable = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def calculate_emi(self):
        P = float(self.amount)
        R = float(self.interest_rate) / (12 * 100)
        N = self.tenure_months

        if R == 0:
            emi = P / N
        else:
            emi = P * R * (1 + R)**N / ((1 + R)**N - 1)

        self.monthly_emi = round(emi, 2)
        self.total_payable = round(emi * N, 2)
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.loan_type} - {self.status}"

class Payment(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('Bank Transfer', 'Bank Transfer'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('UPI', 'UPI'),
        ('Cash', 'Cash')
    ])
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Pending', 'Pending')
    ], default='Success')

    def __str__(self):
        return f"Payment {self.id} - {self.loan.user.username}"