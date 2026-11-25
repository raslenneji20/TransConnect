from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView

from EntreprisesApp.form import EntrepriseForm, EntrepriseUpdateForm
from .auth_forms import DeactivateAccountForm, ProfileForm, RegistrationForm
from .models import Entreprise, Utilisateur
from .permissions import get_user_company, role_required


@role_required(Utilisateur.Role.GERANT, Utilisateur.Role.CHARGEUR)
def home(request):
    from ExpeditionsApp.models import Expedition
    from OffresApp.models import Offre
    from VehiculesApp.models import Vehicule

    company = get_user_company(request.user)
    if not request.user.is_platform_admin and company is None:
        raise PermissionDenied

    if request.user.is_platform_admin:
        entreprises = Entreprise.objects.all()
        expeditions = Expedition.objects.all()
        offres = Offre.objects.all()
        vehicules = Vehicule.objects.all()
    elif request.user.role == Utilisateur.Role.GERANT:
        entreprises = Entreprise.objects.filter(pk=company.pk)
        expeditions = Expedition.objects.filter(statut='publiee')
        offres = Offre.objects.filter(entreprise=company)
        vehicules = Vehicule.objects.filter(entreprise=company)
    else:
        entreprises = Entreprise.objects.filter(pk=company.pk)
        expeditions = Expedition.objects.filter(entreprise=company)
        offres = Offre.objects.filter(expedition__entreprise=company)
        vehicules = Vehicule.objects.none()

    return render(request, 'entreprises/home.html', {
        'entreprises_count': entreprises.count(),
        'expeditions_count': expeditions.count(),
        'offres_count': offres.count(),
        'vehicules_count': vehicules.count(),
    })


@role_required(Utilisateur.Role.GERANT)
def liste_entreprises(request):
    entreprises = Entreprise.objects.all()
    if not request.user.is_platform_admin:
        entreprises = entreprises.filter(gerant=request.user)
    return render(request, 'entreprises/liste.html', {'entreprises': entreprises.order_by('-created_at')})


@role_required(Utilisateur.Role.GERANT)
def detail_entreprise(request, pk):
    entreprises = Entreprise.objects.all()
    if not request.user.is_platform_admin:
        entreprises = entreprises.filter(gerant=request.user)
    entreprise = get_object_or_404(entreprises, pk=pk)
    return render(request, 'entreprises/detail.html', {'entreprise': entreprise})


@method_decorator(role_required(Utilisateur.Role.ADMIN), name='dispatch')
class EntrepriseCreateView(CreateView):
    model = Entreprise
    template_name = 'entreprises/form.html'
    form_class = EntrepriseForm
    success_url = reverse_lazy('entreprises:liste')


@method_decorator(role_required(Utilisateur.Role.GERANT), name='dispatch')
class EntrepriseUpdateView(UpdateView):
    model = Entreprise
    template_name = 'entreprises/update.html'
    form_class = EntrepriseUpdateForm

    def get_queryset(self):
        queryset = Entreprise.objects.all()
        if self.request.user.is_platform_admin:
            return queryset
        return queryset.filter(gerant=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            'entreprises:detail_entreprise',
            kwargs={'pk': self.object.pk},
        )


@method_decorator(role_required(Utilisateur.Role.ADMIN), name='dispatch')
class EntrepriseDeleteView(DeleteView):
    model = Entreprise
    template_name = 'entreprises/confirm_delete.html'
    success_url = reverse_lazy('entreprises:liste')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
    return render(request, 'entreprises/register.html', {'form': form})


@role_required(Utilisateur.Role.GERANT, Utilisateur.Role.CHARGEUR)
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('entreprises:profile')
    return render(request, 'entreprises/profile.html', {'form': form})


@role_required(Utilisateur.Role.GERANT, Utilisateur.Role.CHARGEUR)
def deactivate_account(request):
    form = DeactivateAccountForm(
        request.POST or None,
        user=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            if request.user.is_platform_admin:
                active_admins = Utilisateur.objects.select_for_update().filter(
                    is_active=True,
                ).filter(
                    Q(role=Utilisateur.Role.ADMIN) | Q(is_superuser=True),
                )
                if active_admins.count() <= 1:
                    form.add_error(
                        None,
                        'Le dernier compte administrateur actif ne peut pas être supprimé.',
                    )
                else:
                    _deactivate_user(request.user)
            else:
                _deactivate_user(request.user)

        if not form.errors:
            logout(request)
            return redirect('entreprises:login')
    return render(
        request,
        'entreprises/deactivate_account.html',
        {
            'form': form,
            'deactivation_blocked': (
                request.user.is_platform_admin
                and Utilisateur.objects.filter(is_active=True).filter(
                    Q(role=Utilisateur.Role.ADMIN) | Q(is_superuser=True),
                ).count() <= 1
            ),
        },
    )


def _deactivate_user(user):
    user.is_active = False
    user.set_unusable_password()
    user.save(update_fields=['is_active', 'password', 'updated_at'])
