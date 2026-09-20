from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..forms import LoginForm, MemberRegistrationForm
from ..services import create_member
from ..utils import dashboard_url_for


def home(request):
    if request.user.is_authenticated:
        return redirect(dashboard_url_for(request.user))
    return render(request, 'home.html')


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(dashboard_url_for(request.user))

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        selected_role = form.cleaned_data['role']
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_active and user.role == selected_role:
            login(request, user)
            messages.success(request, f'Welcome back. You are signed in as {user.get_role_display()}.')
            return redirect(dashboard_url_for(user))
        messages.error(request, 'Invalid email, password, or role.')
    elif request.method == 'POST':
        messages.error(request, 'Invalid email, password, or role.')
    return render(request, 'login.html', {'form': form})


@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(dashboard_url_for(request.user))

    form = MemberRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data.copy()
        password = data.pop('password')
        data.pop('confirm_password')
        create_member(password=password, **data)
        messages.success(request, 'Registration successful. Please log in to continue.')
        return redirect('login')
    return render(request, 'register.html', {'form': form})


def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)


def forbidden(request, exception):
    return render(request, 'errors/403.html', status=403)


def server_error(request):
    return render(request, 'errors/500.html', status=500)
