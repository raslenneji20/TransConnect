from django.urls import path
from . import views
app_name = 'expeditions'

urlpatterns = [
    path('', views.liste_expeditions, name='liste'),
    path('create/', views.ExpeditionCreateview.as_view(), name='create'),
    path('delete/<str:reference>/', views.supprimer_expedition, name='delete'),
    path('<str:reference>/', views.detail_expedition, name='detail'),
]