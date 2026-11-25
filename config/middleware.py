from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.middleware.locale import LocaleMiddleware
from django.utils import translation


class FrenchDefaultLocaleMiddleware(LocaleMiddleware):
    def process_request(self, request):
        if settings.LANGUAGE_COOKIE_NAME in request.COOKIES:
            return super().process_request(request)

        translation.activate(settings.LANGUAGE_CODE)
        request.LANGUAGE_CODE = translation.get_language()


class AdminRoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated:
            user = request.user
            if not (user.is_active and user.is_staff and user.is_platform_admin):
                raise PermissionDenied
        return self.get_response(request)
