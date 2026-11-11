from django.urls import path
from . import views

app_name = 'vehicules'

urlpatterns = [
    path('', views.VehiculeListView.as_view(), name='liste'),
    path('<int:pk>/', views.VehiculeDetailView.as_view(), name='detail'),
    path('create/', views.VehiculeCreateView.as_view(), name='create'),
    path('delete/<int:pk>/', views.VehiculesDeleteView.as_view(), name='delete')
]