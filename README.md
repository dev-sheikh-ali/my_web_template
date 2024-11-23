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
sheikh@sheikh:~/Documents/Django_projects/my_web_template$ tree -I 'env|__pycache__|migrations|venv|staticfiles'
.
├── db.sqlite3
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
    ├── social_auth_views.py
    ├── static
    │   └── users
    │       ├── css
    │       │   └── style.css
    │       ├── images
    │       │   └── person.png
    │       └── js
    │           └── scripts.js
    ├── templates
    │   ├── pages
    │   │   ├── base.html
    │   │   ├── footer.html
    │   │   ├── home.html
    │   │   └── navbar.html
    │   └── users
    │       ├── forgot_password.html
    │       ├── login_modal.html
    │       ├── message_modal.html
    │       ├── otp_verification.html
    │       ├── password_reset.html
    │       ├── password_reset_otp.html
    │       ├── profile_modal.html
    │       └── signup_modal.html
    ├── templatetags
    │   └── form_tags.py
    ├── tests.py
    ├── urls.py
    ├── utils.py
    ├── views_auth.py
    ├── views_password.py
    └── views.py

11 directories, 37 files

```

## Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone https://github.com/dev-sheikh-ali/my_web_template.git
    cd my_web_template
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

7. **Access the application:**
    Open your web browser and go to `http://127.0.0.1:8000/`.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.