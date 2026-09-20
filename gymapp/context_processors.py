from .models import User


def role_context(request):
    profile = None
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        if user.role == User.Role.ADMIN:
            profile = getattr(user, 'admin_profile', None)
        elif user.role == User.Role.TRAINER:
            profile = getattr(user, 'trainer_profile', None)
        elif user.role == User.Role.MEMBER:
            profile = getattr(user, 'member_profile', None)
    return {'current_profile': profile}
