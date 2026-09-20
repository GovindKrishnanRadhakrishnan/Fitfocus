from functools import wraps

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from .models import Member
from .utils import dashboard_url_for


def role_required(*roles):
    """Require an authenticated user whose stored role matches one of the allowed roles."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to continue.')
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, 'You are not authorized to access this page.')
                return redirect(dashboard_url_for(request.user))
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def get_assigned_member(trainer, member_id):
    """Return a member assigned to this trainer, or raise Http404."""
    return get_object_or_404(Member, member_id=member_id, trainer=trainer)
