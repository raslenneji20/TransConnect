from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, ListView
from django.urls import reverse_lazy
from .models import Offre
# Create your views here.
class OffreListView(ListView):
    model = Offre
    template_name = 'offres/liste.html'
class OffreCreateView(CreateView):
    model = Offre
    template_name = 'offres/form.html'
    fields = ['expedition', 'entreprise', 'vehicule', 'prix', 'date_proposition']
    def get_success_url(self):
        return reverse_lazy(
            'offres:detail',
            kwargs={'pk': self.object.pk},
        )
class OffreDetailView(DeleteView):
    model = Offre
    template_name = 'offres/detail.html'
    success_url = reverse_lazy('offres:liste')
class OffreDeleteView(DeleteView):
    model = Offre
    template_name = 'offres/confirm_delete.html'
    success_url = reverse_lazy('offres:liste')