from urllib import request

from django.shortcuts import render, get_object_or_404
from .models import Entreprise

def liste_entreprises(request):
    entreprises = (
        Entreprise.objects.all()
        .order_by('-created_at')
    )
    return render(request, 'entreprises/liste.html', {'entreprises': entreprises})

def detail_entreprise(request, matricule_fiscale):
    entreprise = get_object_or_404(Entreprise, matricule_fiscale=matricule_fiscale)
    return render(request, 'entreprises/detail.html', {'entreprise': entreprise})