from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Entreprise


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def check_role(request, *args, **kwargs):
            user = request.user
            if not user.is_active:
                raise PermissionDenied
            if user.is_platform_admin or user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return login_required(check_role)

    return decorator


def get_user_company(user):
    return Entreprise.objects.filter(gerant=user).first()


def get_company_or_forbidden(user):
    company = get_user_company(user)
    if company is None:
        raise PermissionDenied
    return company


