from django.shortcuts import render, redirect
from .models import Member


# HOME PAGE
def home(request):
    return render(request, "home.html")


# REGISTER MEMBER
def register(request):
    if request.method == "POST":

        name = request.POST['name']
        dob = request.POST['dob']
        age = request.POST['age']
        gender = request.POST['gender']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']
        address = request.POST['address']
        height = request.POST['height']
        weight = request.POST['weight']
        goal = request.POST['goal']

        Member.objects.create(
            name=name,
            dob=dob,
            age=age,
            gender=gender,
            email=email,
            password=password,
            phone=phone,
            address=address,
            height=height,
            weight=weight,
            goal=goal
        )

        return redirect('login')

    return render(request, "register.html")


# LOGIN
def login(request):

    if request.method == "POST":

        email = request.POST['email']
        password = request.POST['password']

        member = Member.objects.filter(
            email=email,
            password=password
        ).first()

        if member:
            return redirect('dashboard')

        return render(request, "login.html", {
            "error": "Invalid Email or Password"
        })

    return render(request, "login.html")


# DASHBOARD
def dashboard(request):
    return render(request, "dashboard.html")


# VIEW ALL MEMBERS (ADMIN)
def view_members(request):

    members = Member.objects.all()

    return render(request, "view_members.html", {
        "members": members
    })