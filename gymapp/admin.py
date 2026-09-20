from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Admin, DietPlan, Member, Payment, Progress, Trainer, User, WorkoutPlan


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'role')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    ordering = ('email',)
    list_display = ('email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Admin)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'username', 'user')
    search_fields = ('username', 'user__email')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'fullname', 'phone', 'gender', 'age', 'goal', 'trainer')
    list_filter = ('gender', 'goal', 'trainer')
    search_fields = ('fullname', 'phone', 'user__email')


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('trainer_id', 'fullname', 'phone', 'specialization', 'qualification')
    list_filter = ('specialization',)
    search_fields = ('fullname', 'phone', 'user__email', 'specialization')


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('workout_id', 'workout_name', 'member', 'trainer', 'exercise_type', 'created_at')
    list_filter = ('exercise_type', 'trainer')
    search_fields = ('workout_name', 'member__fullname', 'trainer__fullname')


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ('diet_id', 'member', 'trainer', 'created_at')
    list_filter = ('trainer',)
    search_fields = ('member__fullname', 'trainer__fullname')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'member', 'amount', 'payment_date', 'payment_method', 'payment_status')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('member__fullname', 'member__user__email')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('progress_id', 'member', 'weight', 'updated_date')
    list_filter = ('updated_date',)
    search_fields = ('member__fullname', 'remarks')
