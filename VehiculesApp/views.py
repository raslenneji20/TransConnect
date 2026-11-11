from django.shortcuts import render
from django.views.generic import DeleteView, ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Vehicule
from .form import VehiculeForm
class VehiculeListView(ListView):
    model =Vehicule
    template_name='vehicules/liste.html'
class VehiculeDetailView(DetailView):
    model=Vehicule
    template_name='vehicules/details.html'
class VehiculesDeleteView(DeleteView):
    model=Vehicule
    template_name='vehicules/confirm_delete.html'
    success_url = reverse_lazy('vehicules:liste')
class VehiculeCreateView(CreateView):
    model=Vehicule
    template_name='vehicules/form.html'
    form_class=VehiculeForm 
    def get_success_url(self):
        return reverse_lazy(
            'vehicules:detail',
            kwargs={'pk': self.object.pk},
        )