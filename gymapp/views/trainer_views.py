from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..decorators import role_required
from ..forms import DietPlanForm, ProgressForm, WorkoutPlanForm
from ..models import DietPlan, Progress, User, WorkoutPlan
from ..utils import calculate_bmi


def _trainer_profile(request):
    return request.user.trainer_profile


@role_required(User.Role.TRAINER)
def dashboard(request):
    trainer = _trainer_profile(request)
    assigned_members = trainer.assigned_members.select_related('user')
    context = {
        'trainer': trainer,
        'assigned_count': assigned_members.count(),
        'workout_count': trainer.workout_plans.count(),
        'diet_count': trainer.diet_plans.count(),
        'recent_progress': Progress.objects.filter(member__trainer=trainer).select_related('member')[:5],
        'assigned_members': assigned_members,
    }
    return render(request, 'trainer/dashboard.html', context)


@role_required(User.Role.TRAINER)
def profile(request):
    trainer = _trainer_profile(request)
    return render(request, 'trainer/profile.html', {'trainer': trainer})


@role_required(User.Role.TRAINER)
def members(request):
    trainer = _trainer_profile(request)
    assigned_members = trainer.assigned_members.select_related('user').prefetch_related(
        'workout_plans', 'diet_plans', 'progress_records'
    )
    return render(request, 'trainer/members.html', {'members': assigned_members, 'trainer': trainer})


@role_required(User.Role.TRAINER)
@require_http_methods(['GET', 'POST'])
def workout_add(request):
    trainer = _trainer_profile(request)
    form = WorkoutPlanForm(request.POST or None, trainer=trainer)
    if request.method == 'POST' and form.is_valid():
        plan = form.save(commit=False)
        plan.trainer = trainer
        plan.save()
        messages.success(request, 'Workout plan assigned successfully.')
        return redirect('trainer_workout_add')
    recent = WorkoutPlan.objects.filter(trainer=trainer).select_related('member')[:8]
    return render(request, 'trainer/workout_form.html', {'form': form, 'recent_plans': recent})


@role_required(User.Role.TRAINER)
@require_http_methods(['GET', 'POST'])
def diet_add(request):
    trainer = _trainer_profile(request)
    form = DietPlanForm(request.POST or None, trainer=trainer)
    if request.method == 'POST' and form.is_valid():
        plan = form.save(commit=False)
        plan.trainer = trainer
        plan.save()
        messages.success(request, 'Diet plan assigned successfully.')
        return redirect('trainer_diet_add')
    recent = DietPlan.objects.filter(trainer=trainer).select_related('member')[:8]
    return render(request, 'trainer/diet_form.html', {'form': form, 'recent_plans': recent})


@role_required(User.Role.TRAINER)
@require_http_methods(['GET', 'POST'])
def progress(request):
    trainer = _trainer_profile(request)
    form = ProgressForm(request.POST or None, trainer=trainer)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.save()
        member = record.member
        member.weight = record.weight
        member.save(update_fields=['weight'])
        messages.success(
            request,
            f'Progress updated for {member.fullname}. BMI: {calculate_bmi(record.weight, member.height)}',
        )
        return redirect('trainer_progress')
    member_heights = {
        str(member.member_id): float(member.height)
        for member in trainer.assigned_members.all()
    }
    records = Progress.objects.filter(member__trainer=trainer).select_related('member')[:15]
    return render(
        request,
        'trainer/progress_form.html',
        {'form': form, 'records': records, 'member_heights': member_heights},
    )
