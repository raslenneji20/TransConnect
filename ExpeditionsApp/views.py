from urllib import request

from django.shortcuts import render, get_object_or_404
from .models import Expedition

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
 .select_related('transporteur', 'vehicule')
 .order_by('-date_proposition')
 )
 return render(
 request,
 'expeditions/detail.html',
 {'expedition': expedition, 'offres': offres},
 )