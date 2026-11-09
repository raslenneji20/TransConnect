from django.urls import path
from . import views

app_name = 'vehicules'

urlpatterns = [
    path('', views.liste_vehicules, name='liste'),
    path('<int:pk>/', views.detail_vehicule, name='detail'),
]