from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from .models import Expedition
from django.views.generic import CreateView
from .forms import ExpeditionForm
from django.urls import reverse_lazy

def liste_expeditions(request):
    expeditions = (
        Expedition.objects
        .filter(statut='publiee')
        .select_related('entreprise')
        .order_by('-created_at')
    )
    return render(request, 'expeditions/liste.html', {'expeditions': expeditions})


def detail_expedition(request, reference):
    expedition = get_object_or_404(Expedition, reference=reference)
    offres = (
        expedition.offres
        .select_related('entreprise', 'vehicule')
        .order_by('-date_proposition')
    )
    return render(
        request,
        'expeditions/details.html',   
        {'expedition': expedition, 'offres': offres},
    )


@require_http_methods(["GET", "POST"])
def supprimer_expedition(request, reference):
    expedition = get_object_or_404(Expedition, reference=reference)
    if request.method == "POST":
        expedition.delete()
        return redirect('expeditions:liste')
    return render(
        request,
        'expeditions/confirm_delete.html',
        {'expedition': expedition},
    )
class ExpeditionCreateview(CreateView):
    model=Expedition
    template_name='expeditions/form.html'
    form_class=ExpeditionForm
    def get_success_url(self):
        return reverse_lazy(
            'expeditions:detail',
            kwargs={'reference': self.object.reference},
        )