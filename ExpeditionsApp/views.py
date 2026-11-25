from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from EntreprisesApp.models import Utilisateur
from EntreprisesApp.permissions import get_user_company, role_required
from .models import Expedition
from django.views.generic import CreateView
from .forms import ExpeditionForm
from django.urls import reverse_lazy

@role_required(Utilisateur.Role.GERANT, Utilisateur.Role.CHARGEUR)
def liste_expeditions(request):
    expeditions = Expedition.objects.select_related('entreprise')
    if request.user.is_platform_admin:
        pass
    elif request.user.role == Utilisateur.Role.GERANT:
        expeditions = expeditions.filter(statut='publiee')
    else:
        company = get_user_company(request.user)
        expeditions = expeditions.filter(entreprise=company)
    expeditions = expeditions.order_by('-created_at')
    return render(request, 'expeditions/liste.html', {'expeditions': expeditions})


@role_required(Utilisateur.Role.GERANT, Utilisateur.Role.CHARGEUR)
def detail_expedition(request, reference):
    expeditions = Expedition.objects.select_related('entreprise')
    if not request.user.is_platform_admin:
        company = get_user_company(request.user)
        if request.user.role == Utilisateur.Role.CHARGEUR:
            expeditions = expeditions.filter(entreprise=company)
        else:
            expeditions = expeditions.filter(statut='publiee')
    expedition = get_object_or_404(expeditions, reference=reference)
    offres = expedition.offres.select_related('entreprise', 'vehicule')
    if request.user.role == Utilisateur.Role.GERANT and not request.user.is_platform_admin:
        company = get_user_company(request.user)
        offres = offres.filter(entreprise=company)
    offres = offres.order_by('-date_proposition')
    return render(
        request,
        'expeditions/details.html',   
        {
            'expedition': expedition,
            'offres': offres,
            'can_respond_to_offers': (
                request.user.is_platform_admin
                or request.user.role == Utilisateur.Role.CHARGEUR
            ),
        },
    )


@role_required(Utilisateur.Role.CHARGEUR)
@require_http_methods(["GET", "POST"])
def supprimer_expedition(request, reference):
    expeditions = Expedition.objects.all()
    if not request.user.is_platform_admin:
        company = get_user_company(request.user)
        expeditions = expeditions.filter(entreprise=company)
    expedition = get_object_or_404(expeditions, reference=reference)
    if request.method == "POST":
        expedition.delete()
        return redirect('expeditions:liste')
    return render(
        request,
        'expeditions/confirm_delete.html',
        {'expedition': expedition},
    )
@method_decorator(role_required(Utilisateur.Role.CHARGEUR), name='dispatch')
class ExpeditionCreateview(CreateView):
    model=Expedition
    template_name='expeditions/form.html'
    form_class=ExpeditionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'expeditions:detail',
            kwargs={'reference': self.object.reference},
        )
