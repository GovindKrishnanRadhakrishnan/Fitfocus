from django.urls import path

from .views import admin_views, auth_views, member_views, trainer_views

urlpatterns = [
    path('', auth_views.home, name='home'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),

    path('admin-dashboard/', admin_views.dashboard, name='admin_dashboard'),
    path('admin/members/', admin_views.members_list, name='admin_members'),
    path('admin/members/add/', admin_views.member_add, name='admin_member_add'),
    path('admin/members/<int:member_id>/', admin_views.member_detail, name='admin_member_detail'),
    path('admin/trainers/', admin_views.trainers_list, name='admin_trainers'),
    path('admin/trainers/add/', admin_views.trainer_add, name='admin_trainer_add'),
    path('admin/trainers/manage/', admin_views.trainers_manage, name='admin_trainers_manage'),
    path('admin/trainers/<int:trainer_id>/edit/', admin_views.trainer_edit, name='admin_trainer_edit'),
    path('admin/assign-trainer/', admin_views.assign_trainer, name='admin_assign_trainer'),
    path('admin/payments/', admin_views.payments, name='admin_payments'),

    path('trainer-dashboard/', trainer_views.dashboard, name='trainer_dashboard'),
    path('trainer/profile/', trainer_views.profile, name='trainer_profile'),
    path('trainer/members/', trainer_views.members, name='trainer_members'),
    path('trainer/workout/add/', trainer_views.workout_add, name='trainer_workout_add'),
    path('trainer/diet/add/', trainer_views.diet_add, name='trainer_diet_add'),
    path('trainer/progress/', trainer_views.progress, name='trainer_progress'),

    path('member-dashboard/', member_views.dashboard, name='member_dashboard'),
    path('member/profile/', member_views.profile, name='member_profile'),
    path('member/workout/', member_views.workout, name='member_workout'),
    path('member/diet/', member_views.diet, name='member_diet'),
    path('member/progress/', member_views.progress, name='member_progress'),
    path('member/payments/', member_views.payments, name='member_payments'),
]
