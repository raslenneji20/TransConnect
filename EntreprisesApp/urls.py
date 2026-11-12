from django.urls import path
from . import views
app_name = 'entreprises'
urlpatterns = [
path('', views.liste_entreprises, name='liste'),
path('create/',views.EntrepriseCreateView.as_view(), name='create'),
path('delete/<int:pk>/', views.EntrepriseDeleteView.as_view(), name='delete'),
path('<int:pk>/', views.detail_entreprise, name='detail_entreprise'),
]