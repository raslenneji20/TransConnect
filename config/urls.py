from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('expeditions/', include('ExpeditionsApp.urls')),
    path('entreprises/', include('EntreprisesApp.urls')),
    path('vehicules/', include('VehiculesApp.urls')),
    path('offres/', include('OffresApp.urls')),
]