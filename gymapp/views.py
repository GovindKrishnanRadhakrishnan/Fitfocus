from django.shortcuts import render, redirect
from .models import Member, Trainer, Admin

def home(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        dob = request.POST.get('dob')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        address = request.POST.get('address')
        goal = request.POST.get('goal')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})

        if Member.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "Email is already registered"})

        Member.objects.create(
            name=fullname,
            dob=dob,
            age=age,
            gender=gender,
            email=email,
            phone=phone,
            height=height,
            weight=weight,
            address=address,
            goal=goal,
            password=password
        )
        return redirect('login')

    return render(request, "register.html")

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')  # 'admin', 'trainer', 'member'

        if role == 'admin':
            # Create default admin user if none exists
            if not Admin.objects.filter(email=email).exists() and email == "admin@fitfocus.com" and password == "admin123":
                Admin.objects.create(name="Admin User", email=email, password=password)
            
            admin = Admin.objects.filter(email=email, password=password).first()
            if admin:
                request.session['role'] = 'admin'
                request.session['email'] = email
                request.session['name'] = admin.name
                return redirect('admin_dashboard')
        
        elif role == 'trainer':
            trainer = Trainer.objects.filter(email=email, password=password).first()
            if trainer:
                request.session['role'] = 'trainer'
                request.session['email'] = email
                request.session['name'] = trainer.name
                return redirect('trainer_dashboard')
                
        elif role == 'member':
            member = Member.objects.filter(email=email, password=password).first()
            if member:
                request.session['role'] = 'member'
                request.session['email'] = email
                request.session['name'] = member.name
                return redirect('client_dashboard')

        return render(request, "login.html", {
            "error": "Invalid Email, Password, or Role"
        })

    return render(request, "login.html")

def dashboard(request):
    role = request.session.get('role')
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'trainer':
        return redirect('trainer_dashboard')
    elif role == 'member':
        return redirect('client_dashboard')
    return redirect('login')

def admin_dashboard(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    return render(request, 'admindash.html')

def trainer_dashboard(request):
    if request.session.get('role') != 'trainer':
        return redirect('login')
    return render(request, 'trainer_dashboard.html')

def client_dashboard(request):
    if request.session.get('role') != 'member':
        return redirect('login')
    return render(request, 'client_dashboard.html')

def view_members(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    members = Member.objects.all()
    return render(request, "view_members.html", {"members": members})

def logout(request):
    request.session.flush()
    return redirect('home')