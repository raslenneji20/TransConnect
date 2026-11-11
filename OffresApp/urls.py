from django.urls import path
from . import views

app_name = 'offres'

urlpatterns = [
    path('', views.OffreListView.as_view(), name='liste'),
    path('delete/<int:pk>/', views.OffreDeleteView.as_view(), name='delete'),

    path('<int:pk>/', views.OffreDetailView.as_view(), name='detail'),
    path('create/', views.OffreCreateView.as_view(), name='create'),
]