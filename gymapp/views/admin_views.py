from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from ..decorators import role_required
from ..forms import AssignTrainerForm, MemberRegistrationForm, PaymentForm, TrainerForm
from ..models import Member, Payment, Trainer, User
from ..services import create_member, create_trainer, update_trainer


@role_required(User.Role.ADMIN)
def dashboard(request):
    members = Member.objects.select_related('trainer', 'user').order_by('-member_id')
    payments = Payment.objects.select_related('member')
    context = {
        'total_members': members.count(),
        'total_trainers': Trainer.objects.count(),
        'total_payments': payments.count(),
        'payment_total_amount': payments.aggregate(total=Sum('amount'))['total'] or 0,
        'recent_members': members[:5],
    }
    return render(request, 'admin/dashboard.html', context)


@role_required(User.Role.ADMIN)
def members_list(request):
    members = Member.objects.select_related('trainer', 'user').order_by('fullname')
    return render(request, 'admin/members.html', {'members': members})


@role_required(User.Role.ADMIN)
def member_detail(request, member_id):
    member = get_object_or_404(Member.objects.select_related('trainer', 'user'), member_id=member_id)
    context = {
        'member': member,
        'latest_workout': member.workout_plans.select_related('trainer').first(),
        'latest_diet': member.diet_plans.select_related('trainer').first(),
        'progress_records': member.progress_records.all()[:10],
        'payments': member.payments.all()[:10],
        'bmi': member.calculate_bmi(),
    }
    return render(request, 'admin/member_detail.html', context)


@role_required(User.Role.ADMIN)
@require_http_methods(['GET', 'POST'])
def member_add(request):
    form = MemberRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data.copy()
        password = data.pop('password')
        data.pop('confirm_password')
        create_member(password=password, **data)
        messages.success(request, 'Member added successfully.')
        return redirect('admin_members')
    return render(request, 'admin/add_member.html', {'form': form})


@role_required(User.Role.ADMIN)
def trainers_list(request):
    trainers = Trainer.objects.select_related('user').order_by('fullname')
    return render(request, 'admin/trainers.html', {'trainers': trainers})


@role_required(User.Role.ADMIN)
def trainers_manage(request):
    trainers = Trainer.objects.select_related('user').prefetch_related('assigned_members').order_by('fullname')
    return render(request, 'admin/manage_trainers.html', {'trainers': trainers})


@role_required(User.Role.ADMIN)
@require_http_methods(['GET', 'POST'])
def trainer_add(request):
    form = TrainerForm(request.POST or None, require_password=True)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data.copy()
        password = data.pop('password')
        create_trainer(password=password, **data)
        messages.success(request, 'Trainer added successfully.')
        return redirect('admin_trainers_manage')
    return render(request, 'admin/add_trainer.html', {'form': form, 'title': 'Add Trainer'})


@role_required(User.Role.ADMIN)
@require_http_methods(['GET', 'POST'])
def trainer_edit(request, trainer_id):
    trainer = get_object_or_404(Trainer, trainer_id=trainer_id)
    form = TrainerForm(request.POST or None, instance=trainer, require_password=False)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data.copy()
        password = data.pop('password') or None
        email = data.pop('email')
        update_trainer(trainer, password=password, email=email, **data)
        messages.success(request, 'Trainer information updated.')
        return redirect('admin_trainers_manage')
    return render(request, 'admin/add_trainer.html', {'form': form, 'title': 'Manage Trainer', 'trainer': trainer})


@role_required(User.Role.ADMIN)
@require_http_methods(['GET', 'POST'])
def assign_trainer(request):
    form = AssignTrainerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        member = form.cleaned_data['member']
        trainer = form.cleaned_data['trainer']
        member.trainer = trainer
        member.save(update_fields=['trainer'])
        messages.success(request, f'{trainer.fullname} has been assigned to {member.fullname}.')
        return redirect('admin_assign_trainer')
    assignments = Member.objects.select_related('trainer', 'user').order_by('fullname')
    return render(request, 'admin/assign_trainer.html', {'form': form, 'assignments': assignments})


@role_required(User.Role.ADMIN)
@require_http_methods(['GET', 'POST'])
def payments(request):
    form = PaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Payment record saved.')
        return redirect('admin_payments')
    payment_list = Payment.objects.select_related('member').all()
    return render(request, 'admin/payments.html', {'form': form, 'payments': payment_list})
