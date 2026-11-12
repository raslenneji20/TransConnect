from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation


class FrenchDefaultLocaleMiddleware(LocaleMiddleware):
    def process_request(self, request):
        if settings.LANGUAGE_COOKIE_NAME in request.COOKIES:
            return super().process_request(request)

        translation.activate(settings.LANGUAGE_CODE)
        request.LANGUAGE_CODE = translation.get_language()
