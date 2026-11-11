from urllib import request

from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView

from EntreprisesApp.form import EntrepriseForm
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
class EntrepriseCreateView(CreateView):
    model=Entreprise
    template_name='entreprises/form.html'
    form_class=EntrepriseForm
class EntrepriseDeleteView(DeleteView):
    model=Entreprise
    template_name='entreprises/confirm_delete.html'
    success_url = reverse_lazy('entreprises:liste')