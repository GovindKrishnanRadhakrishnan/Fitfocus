from django.shortcuts import render

from ..decorators import role_required
from ..models import User
from ..utils import bmi_category, calculate_bmi


def _member_profile(request):
    return request.user.member_profile


@role_required(User.Role.MEMBER)
def dashboard(request):
    member = _member_profile(request)
    latest_progress = member.progress_records.first()
    current_weight = latest_progress.weight if latest_progress else member.weight
    bmi = calculate_bmi(current_weight, member.height)
    latest_payment = member.payments.first()
    context = {
        'member': member,
        'current_weight': current_weight,
        'bmi': bmi,
        'bmi_category': bmi_category(bmi),
        'latest_workout': member.workout_plans.select_related('trainer').first(),
        'latest_diet': member.diet_plans.select_related('trainer').first(),
        'latest_payment': latest_payment,
        'assigned_trainer': member.trainer,
    }
    return render(request, 'member/dashboard.html', context)


@role_required(User.Role.MEMBER)
def profile(request):
    member = _member_profile(request)
    bmi = member.calculate_bmi()
    return render(
        request,
        'member/profile.html',
        {'member': member, 'bmi': bmi, 'bmi_category': bmi_category(bmi)},
    )


@role_required(User.Role.MEMBER)
def workout(request):
    member = _member_profile(request)
    plans = member.workout_plans.select_related('trainer')
    return render(request, 'member/workout.html', {'member': member, 'plans': plans, 'latest': plans.first()})


@role_required(User.Role.MEMBER)
def diet(request):
    member = _member_profile(request)
    plans = member.diet_plans.select_related('trainer')
    return render(request, 'member/diet.html', {'member': member, 'plans': plans, 'latest': plans.first()})


@role_required(User.Role.MEMBER)
def progress(request):
    member = _member_profile(request)
    records = member.progress_records.all()
    latest = records.first()
    current_weight = latest.weight if latest else member.weight
    bmi = calculate_bmi(current_weight, member.height)
    return render(
        request,
        'member/progress.html',
        {
            'member': member,
            'records': records,
            'latest': latest,
            'current_weight': current_weight,
            'bmi': bmi,
            'bmi_category': bmi_category(bmi),
        },
    )


@role_required(User.Role.MEMBER)
def payments(request):
    member = _member_profile(request)
    payment_list = member.payments.all()
    return render(request, 'member/payments.html', {'member': member, 'payments': payment_list})
