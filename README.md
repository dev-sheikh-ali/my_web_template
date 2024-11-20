# My Web Template

This is a Django project template focused on user management. It leverages Django’s built-in capabilities and popular libraries such as Django REST Framework, Bootstrap, and Python's secrets for OTP to create a flexible and consistent user experience.

## Features

- User Signup, Login, and Logout
- Email Verification via OTP and Verification Link
- Profile Management with Modal for Editing User Information
- Password Reset Functionality
- Responsive Frontend using Bootstrap

## Project Structure

```bash
user@user:~/Documents/Django_projects/my_web_template$ tree -I 'env|__pycache__|migrations|venv'
.
├── manage.py
├── my_web_template
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
└── users
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── static
    │   ├── css
    │   │   └── style.css
    │   └── js
    │       └── scripts.js
    ├── templates
    │   ├── pages
    │   │   ├── base.html
    │   │   ├── footer.html
    │   │   ├── home.html
    │   │   └── navbar.html
    │   └── users
    │       ├── email_verification.html
    │       ├── forgot_password.html
    │       ├── login_modal.html
    │       ├── otp_verification.html
    │       ├── password_reset.html
    │       ├── profile_modal.html
    │       └── signup_modal.html
    ├── templatetags
    │   └── form_tags.py
    ├── tests.py
    ├── urls.py
    ├── utils.py
    └── views.py

9 directories, 31 files
sheikh@sheikh:~/Documents/Django_projects/my_web_template$ 

'''