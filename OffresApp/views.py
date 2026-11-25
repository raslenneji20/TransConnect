from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from EntreprisesApp.models import Utilisateur
from EntreprisesApp.permissions import get_user_company, role_required
from .forms import OffreForm
from .models import Offre


@method_decorator(
    role_required(Utilisateur.Role.GERANT, Utilisateur.Role.CHARGEUR),
    name='dispatch',
)
class OffreListView(ListView):
    model = Offre
    template_name = 'offres/liste.html'

    def get_queryset(self):
        queryset = Offre.objects.select_related('expedition', 'entreprise', 'vehicule')
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        company = get_user_company(user)
        if company is None:
            return queryset.none()
        if user.role == Utilisateur.Role.GERANT:
            return queryset.filter(entreprise=company)
        return queryset.filter(expedition__entreprise=company)


@method_decorator(role_required(Utilisateur.Role.GERANT), name='dispatch')
class OffreCreateView(CreateView):
    model = Offre
    template_name = 'offres/form.html'
    form_class = OffreForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_platform_admin:
            company = get_user_company(request.user)
            if company is None or company.type_entreprise != 'transporteur':
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_platform_admin:
            company = get_user_company(self.request.user)
            if company is None or company.type_entreprise != 'transporteur':
                raise PermissionDenied
            form.instance.entreprise = company
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'offres:detail',
            kwargs={'pk': self.object.pk},
        )


@method_decorator(
    role_required(Utilisateur.Role.GERANT, Utilisateur.Role.CHARGEUR),
    name='dispatch',
)
class OffreDetailView(DetailView):
    model = Offre
    template_name = 'offres/detail.html'

    def get_queryset(self):
        queryset = Offre.objects.select_related('expedition', 'entreprise', 'vehicule')
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        company = get_user_company(user)
        if company is None:
            return queryset.none()
        if user.role == Utilisateur.Role.GERANT:
            return queryset.filter(entreprise=company)
        return queryset.filter(expedition__entreprise=company)


@method_decorator(role_required(Utilisateur.Role.GERANT), name='dispatch')
class OffreDeleteView(DeleteView):
    model = Offre
    template_name = 'offres/confirm_delete.html'
    success_url = reverse_lazy('offres:liste')

    def get_queryset(self):
        queryset = Offre.objects.all()
        if self.request.user.is_platform_admin:
            return queryset
        company = get_user_company(self.request.user)
        if company is None:
            return queryset.none()
        return queryset.filter(entreprise=company)


@role_required(Utilisateur.Role.CHARGEUR)
@require_POST
def repondre_offre(request, pk):
    offres = Offre.objects.select_related('expedition')
    if not request.user.is_platform_admin:
        company = get_user_company(request.user)
        offres = offres.filter(expedition__entreprise=company)
    offre = get_object_or_404(offres, pk=pk, statut='proposee')

    action = request.POST.get('action')
    if action not in ('acceptee', 'refusee'):
        raise PermissionDenied
    if offre.expedition.statut != 'publiee':
        raise PermissionDenied

    offre.statut = action
    offre.save()
    messages.success(request, 'Votre réponse à l’offre a été enregistrée.')
    return redirect(
        'expeditions:detail',
        reference=offre.expedition.reference,
    )