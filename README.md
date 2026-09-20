<<<<<<< HEAD
# FitFocus Gym Management System

## 1. Project Overview

FitFocus is a web-based Gym Management System that digitizes day-to-day gym operations. It was built as a server-rendered Django application so that administrators, trainers, and members can work in one place instead of paper records or disconnected spreadsheets.

The system is developed with:

- Python
- Django
- SQLite
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

FitFocus provides separate, role-based functionality for:

- **Admin** – gym operations, people, and payments
- **Trainer** – assigned members, workout plans, diet plans, and progress
- **Member** – registration, profile, assigned plans, progress, and payment details

The application digitizes:

- Member management
- Trainer management
- Workout planning
- Diet planning
- Progress tracking
- Payment records

Each role only sees the screens and data that belong to that role. Authorization is enforced in Django views, not only by hiding buttons in the user interface.

The project starts empty of sample members and trainers. After installation, only one administrator account exists. Real members register themselves, and the administrator creates real trainers through the application.

## 2. Features

### Admin

- Log in with email, password, and the Admin role
- Open the Admin Dashboard, which shows totals for members, trainers, and payments, plus recent members
- Add members (in addition to public member registration)
- View the member list and individual member details
- Add trainers
- Manage and update trainer information
- Assign a trainer to a member
- View payment records and create new payment records

Dashboard shortcuts include: Add Members, View Members, Add Trainers, Manage Trainers, Assign Trainers, and View Payments.

### Trainer

- Log in with email, password, and the Trainer role
- View the trainer profile
- View only members assigned to that trainer
- Assign a workout plan to an assigned member
- Assign a diet plan to an assigned member
- Update member progress (weight, remarks, and date)
- BMI is calculated automatically from the member’s height and the recorded weight. Trainers do not need to enter BMI by hand

A trainer cannot manage members who are not assigned to them.

### Member

- Register through `/register/`
- Log in with email, password, and the Member role
- View their own profile
- View assigned workout plans
- View assigned diet plans
- Track progress history, including current weight and BMI
- View their own payment details

New members start with empty workout, diet, progress, and payment pages until a trainer or administrator records real data. The application does not generate fake records for new members.

## 3. Technology Stack

| Technology | How it is used |
| --- | --- |
| **Python** | Application language |
| **Django** | Web framework: routing, views, forms, authentication, and ORM |
| **SQLite** | Default local database file (`db.sqlite3`) |
| **HTML5** | Page structure in Django templates |
| **CSS3** | Custom FitFocus styling in `static/css/style.css` |
| **JavaScript** | Small helpers in `static/js/main.js` (age from date of birth, automatic BMI on the progress form) |
| **Bootstrap 5** | Responsive layout, forms, tables, cards, and alerts |

Additional Django capabilities used by the project:

- **Django ORM** – all database access goes through models. Raw SQL is not used for application queries.
- **Django authentication** – email/password login using a custom `User` model (`USERNAME_FIELD = email`).
- **Django templates** – server-side HTML with template inheritance (`base.html`, `dashboard_base.html`).
- **Session authentication** – after a successful login, Django stores the user in the session.
- **CSRF protection** – state-changing forms include `{% csrf_token %}`. Logout is POST.

## 4. Project Structure

```text
FitFocus-Gym-Management-System/
│
├── manage.py                 # Django command-line entry point
├── requirements.txt          # Python dependencies (Django)
├── README.md                 # This file
├── db.sqlite3                # Created locally after migrate (not required in source control)
│
├── fitt/                     # Django project package
│   ├── settings.py           # Apps, SQLite, auth user model, templates, static files
│   ├── urls.py               # Root URLs, including gymapp and /django-admin/
│   ├── wsgi.py
│   └── asgi.py
│
├── gymapp/                   # Main application
│   ├── models.py             # User, Admin, Trainer, Member, plans, progress, payments
│   ├── forms.py              # Login, registration, trainer, assignment, plan, payment forms
│   ├── services.py           # Helpers that create members, trainers, and the admin user
│   ├── decorators.py         # Role-based view protection
│   ├── utils.py              # BMI calculation and dashboard redirects
│   ├── admin.py              # Django admin inspection for developers
│   ├── urls.py               # Application URL routes
│   ├── context_processors.py # Current profile in templates
│   ├── tests.py              # Automated tests
│   ├── views/
│   │   ├── auth_views.py     # Home, login, logout, register
│   │   ├── admin_views.py    # Admin dashboard and management pages
│   │   ├── trainer_views.py  # Trainer dashboard and forms
│   │   └── member_views.py   # Member dashboard and personal pages
│   └── management/commands/
│       └── create_initial_admin.py
│
├── templates/                # HTML templates used by the live application
│   ├── base.html
│   ├── dashboard_base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── admin/
│   ├── trainer/
│   ├── member/
│   └── errors/
│
└── static/
    ├── css/style.css
    └── js/main.js
```

**Important files**

- `manage.py` – run the server, migrations, tests, and the initial admin command
- `fitt/settings.py` – project configuration; `AUTH_USER_MODEL` is `gymapp.User`
- `gymapp/models.py` – database design
- `gymapp/views/` – request handling split by role
- `gymapp/decorators.py` – `role_required` checks the stored user role on every protected view
- `templates/` – the pages users actually see (`admin/`, `trainer/`, and `member/` folders)

The live templates are the files under `templates/admin/`, `templates/trainer/`, `templates/member/`, plus `home.html`, `login.html`, `register.html`, and the shared bases. Older leftover HTML files in `templates/` are not used by the current URL configuration.

## 5. Database Design

The database is SQLite, accessed through Django models.

### User

Custom user model used for login. Email is unique and is the username field. Role is one of `admin`, `trainer`, or `member`. The password is stored as a Django hash.

### Admin

Profile linked to a User (`OneToOne`). Fields include `admin_id` and `username`.

### Trainer

Profile linked to a User (`OneToOne`). Fields include `trainer_id`, full name, phone, specialization, and qualification. Email comes from the related User.

### Member

Profile linked to a User (`OneToOne`). Fields include `member_id`, full name, date of birth, age, gender, unique phone, address, height (cm), weight (kg), and fitness goal. A member may have one assigned trainer (`ForeignKey`, optional).

### WorkoutPlan

Belongs to a member and a trainer. Stores workout name, exercise type, duration, sets, repetitions, and instructions.

### DietPlan

Belongs to a member and a trainer. Stores breakfast, lunch, dinner, snacks, and instructions.

### Progress

Belongs to a member. Stores weight, remarks, and updated date. BMI is not stored as a separate column; it is calculated from the member’s height and the progress weight: `BMI = weight_kg / (height_m)^2`.

### Payment

Belongs to a member. Stores amount, payment date, payment method, and payment status.

### Relationships used in the code

- An administrator manages members and trainers through admin views
- An administrator assigns a trainer to a member (`Member.trainer`)
- A trainer has assigned members (`Trainer.assigned_members`)
- A trainer creates workout plans and diet plans for a member
- A trainer updates progress records for assigned members
- A member has workout plans, diet plans, progress records, and payments
- Users authenticate through Django authentication; Admin, Trainer, and Member rows point at a User with `OneToOneField`

## 6. Authentication and Security

- Login requires email, password, and role
- Django session authentication is used after a successful login
- The selected role must match the role stored on the user. A member cannot log in as Admin by choosing that radio button
- Passwords are hashed with Django’s password hasher (`set_password` / `create_user`). They are never stored as plaintext in the database
- CSRF tokens protect POST forms; logout is a POST request
- Server-side validation is implemented with Django forms (required fields, unique email/phone, matching passwords, numeric height and weight)
- `@role_required` decorators block the wrong role from opening another role’s URLs
- Trainers can only select and update members assigned to them
- Member pages load data from `request.user.member_profile`, so a member cannot open another member’s records by changing a URL
- Database work uses the Django ORM

The initial administrator password is hashed when `create_initial_admin` runs. The value in this README is the password you type on the login page, not the value stored in SQLite.

## 7. Installation

These steps are for a fresh computer.

### Prerequisites

- Python 3.10 or later (`python --version`)
- pip (included with Python)
- Git, only if you are cloning the project from a Git repository

### Step 1 – Get the project

Copy the `FitFocus-Gym-Management-System` folder onto the computer, or clone it if it is in Git:

```bash
git clone <repository-url>
```

### Step 2 – Open the project directory

**Windows (Command Prompt or PowerShell):**

```bat
cd FitFocus-Gym-Management-System
```

**Linux / macOS:**

```bash
cd FitFocus-Gym-Management-System
```

### Step 3 – Create and activate a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4 – Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5 – Apply database migrations

This creates the SQLite file and all tables. It does not insert members, trainers, or sample gym data.

```bash
python manage.py migrate
```

### Step 6 – Create the initial administrator

```bash
python manage.py create_initial_admin
```

This command:

- Creates `admin@gmail.com` with the Admin role if that account does not exist
- Stores the password using Django’s hasher
- Does nothing if the administrator already exists (safe to run more than once)
- Does not create members, trainers, workout plans, diet plans, progress records, or payments

### Step 7 – Start the development server

```bash
python manage.py runserver
```

Open a browser at:

http://127.0.0.1:8000/

Stop the server with `Ctrl+C`.

## 8. Initial Administrator Login

Use the FitFocus login page (`/login/`), not a separate demo account list.

| Field | Value |
| --- | --- |
| Email | admin@gmail.com |
| Password | admin123 |
| Role | Admin |

After login, the administrator is sent to `/admin-dashboard/`.

There are no default trainers or members. The administrator adds trainers from **Add Trainers**. Members create their own accounts at `/register/`, or the administrator can add a member from **Add Members**.

## 9. How to Use the System

Typical first-time workflow:

1. Install, migrate, create the initial admin, and start the server
2. Log in as Admin
3. Add one or more trainers
4. Ask gym members to register at `/register/`
5. Assign trainers to members
6. Trainers log in and assign workout plans, diet plans, and progress updates
7. Members log in to view their profile, plans, progress, and payments
8. Admin records payments on **View Payments**

Member registration fields: full name, date of birth, age, gender, phone, email, height (cm), weight (kg), address, fitness goal, password, and confirm password.

A newly registered member can log in immediately. Workout, diet, progress, and payment pages stay empty until real records are created in the application.

## 10. Main URLs

| URL | Purpose |
| --- | --- |
| `/` | Landing page |
| `/login/` | Login (email, password, role) |
| `/logout/` | Logout (POST) |
| `/register/` | Member registration |
| `/admin-dashboard/` | Admin dashboard |
| `/admin/members/` | View members |
| `/admin/members/add/` | Add a member |
| `/admin/trainers/add/` | Add a trainer |
| `/admin/trainers/manage/` | Manage trainers |
| `/admin/assign-trainer/` | Assign a trainer to a member |
| `/admin/payments/` | View and create payments |
| `/trainer-dashboard/` | Trainer dashboard |
| `/trainer/profile/` | Trainer profile |
| `/trainer/members/` | Assigned members |
| `/trainer/workout/add/` | Assign workout plan |
| `/trainer/diet/add/` | Assign diet plan |
| `/trainer/progress/` | Update member progress |
| `/member-dashboard/` | Member dashboard |
| `/member/profile/` | Member profile |
| `/member/workout/` | Assigned workout plan |
| `/member/diet/` | Assigned diet plan |
| `/member/progress/` | Progress tracking |
| `/member/payments/` | Payment details |
| `/django-admin/` | Django’s built-in admin for developers inspecting records |

`/django-admin/` is separate from the gym Admin pages under `/admin/...`.

## 11. Testing

From the project directory, with dependencies installed:

```bash
python manage.py check
python manage.py test
```

The test suite creates its own temporary database. It does not depend on demo gym members or trainers in `db.sqlite3`.

## 12. Notes

- Height is stored in centimetres. BMI uses height converted to metres.
- Logout uses POST (the navbar Logout button).
- Member and trainer passwords entered in the UI must satisfy Django’s password validators (at least 8 characters, not entirely numeric, and not a common password).
- The initial administrator is created by `create_initial_admin` and is intended for first access to the system.
- SQLite is appropriate for local use. Change `DATABASES` in `fitt/settings.py` only if you deliberately move to another database engine.
=======
# Fitfocus
A full-stack gym management system built with Python Django and SQLite, featuring role-based dashboards for admins, trainers, and members, with workout, diet, progress, and payment management.
>>>>>>> 9d2a6a859b6f2a7cf71ac03cd076d240ceb7730d
