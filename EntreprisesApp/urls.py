from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
app_name = 'entreprises'
urlpatterns = [
path('home/', views.home, name='home_alias'),
path('', views.liste_entreprises, name='liste'),
path('create/',views.EntrepriseCreateView.as_view(), name='create'),
path('update/<int:pk>/', views.EntrepriseUpdateView.as_view(), name='update'),
path('delete/<int:pk>/', views.EntrepriseDeleteView.as_view(), name='delete'),
path('login/',auth_views.LoginView.as_view(template_name='entreprises/login.html'), name='login'),
path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='entreprises/password_reset_form.html',
        email_template_name='entreprises/password_reset_email.html',
        subject_template_name='entreprises/password_reset_subject.txt',
        success_url=reverse_lazy('entreprises:password_reset_done'),
    ),
    name='password_reset',
),
path(
    'password-reset/done/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='entreprises/password_reset_done.html',
    ),
    name='password_reset_done',
),
path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='entreprises/password_reset_confirm.html',
        success_url=reverse_lazy('entreprises:password_reset_complete'),
    ),
    name='password_reset_confirm',
),
path(
    'reset/complete/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='entreprises/password_reset_complete.html',
    ),
    name='password_reset_complete',
),
path('register/', views.register, name='register'),
path('profile/', views.profile, name='profile'),
path('deactivate/', views.deactivate_account, name='deactivate_account'),
path('logout/', auth_views.LogoutView.as_view(), name='logout'),
path('<int:pk>/', views.detail_entreprise, name='detail_entreprise'),
]