# Email Configuration Guide for Loan Management System

## 📧 Email Setup Instructions

### 1. Configure Email Settings in `settings.py`

Update the following email configuration in your `loanproject/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # For Gmail. Use your email provider's SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your app password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Replace with your email
```

### 2. Gmail Setup (Most Common)

#### For Gmail Users:
1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this 16-character password as `EMAIL_HOST_PASSWORD`

#### Alternative Gmail Settings:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
```

### 3. Other Email Providers

#### Outlook/Hotmail:
```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### Yahoo:
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### Custom SMTP:
```python
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587  # or 465
EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True
```

### 4. Testing Email Configuration

Run this command to test email sending:

```bash
python manage.py shell
```

Then in the shell:
```python
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'Test message body',
    'your-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

### 5. Email Templates Created

The following email templates have been created in `loanapp/templates/emails/`:

- `loan_submitted.html/txt` - Sent when loan application is submitted
- `loan_approved.html/txt` - Sent when loan is approved
- `loan_rejected.html/txt` - Sent when loan is rejected
- `loan_disbursed.html/txt` - Sent when loan funds are disbursed
- `payment_confirmation.html/txt` - Sent when payment is made

### 6. Email Triggers

Emails are automatically sent when:

1. **Loan Application Submitted** → `loan_submitted` email
2. **Loan Status Changed to Approved** → `loan_approved` email
3. **Loan Status Changed to Rejected** → `loan_rejected` email
4. **Loan Status Changed to Disbursed** → `loan_disbursed` email
5. **Payment Made** → `payment_confirmation` email

### 7. Troubleshooting

#### Common Issues:

1. **SMTP Authentication Error**:
   - Verify email credentials
   - Check if app password is correct (for Gmail)
   - Ensure 2FA is enabled for Gmail app passwords

2. **Connection Timeout**:
   - Check internet connection
   - Verify EMAIL_HOST and EMAIL_PORT
   - Try different port (587 vs 465)

3. **Emails Not Sending**:
   - Check Django logs for errors
   - Verify EMAIL_BACKEND setting
   - Test with simple send_mail() function

#### Debug Mode:
Add this to settings.py for debugging:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
This will print emails to console instead of sending them.

### 8. Security Notes

- Never commit email credentials to version control
- Use environment variables for production:
```python
import os
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

- Consider using services like SendGrid, Mailgun, or AWS SES for production

---

## 🎯 Features Added

✅ **Automatic Email Notifications** for all loan lifecycle events
✅ **Professional HTML Email Templates** with responsive design
✅ **Plain Text Fallbacks** for email clients that don't support HTML
✅ **Payment Confirmations** when users make loan payments
✅ **Status Update Emails** when admins change loan status

Your loan management system now provides complete email communication with applicants!