from django.shortcuts import render
from django.views.generic import DeleteView, ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from EntreprisesApp.models import Utilisateur
from EntreprisesApp.permissions import get_user_company, role_required
from .models import Vehicule
from .form import VehiculeForm


@method_decorator(role_required(Utilisateur.Role.GERANT), name='dispatch')
class VehiculeListView(ListView):
    model =Vehicule
    template_name='vehicules/liste.html'

    def get_queryset(self):
        queryset = Vehicule.objects.select_related('entreprise')
        if self.request.user.is_platform_admin:
            return queryset
        company = get_user_company(self.request.user)
        return queryset.filter(entreprise=company) if company else queryset.none()


@method_decorator(role_required(Utilisateur.Role.GERANT), name='dispatch')
class VehiculeDetailView(DetailView):
    model=Vehicule
    template_name='vehicules/details.html'

    def get_queryset(self):
        queryset = Vehicule.objects.select_related('entreprise')
        if self.request.user.is_platform_admin:
            return queryset
        company = get_user_company(self.request.user)
        return queryset.filter(entreprise=company) if company else queryset.none()


@method_decorator(role_required(Utilisateur.Role.GERANT), name='dispatch')
class VehiculesDeleteView(DeleteView):
    model=Vehicule
    template_name='vehicules/confirm_delete.html'
    success_url = reverse_lazy('vehicules:liste')

    def get_queryset(self):
        queryset = Vehicule.objects.all()
        if self.request.user.is_platform_admin:
            return queryset
        company = get_user_company(self.request.user)
        return queryset.filter(entreprise=company) if company else queryset.none()


@method_decorator(role_required(Utilisateur.Role.GERANT), name='dispatch')
class VehiculeCreateView(CreateView):
    model=Vehicule
    template_name='vehicules/form.html'
    form_class=VehiculeForm 

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

    def get_success_url(self):
        return reverse_lazy(
            'vehicules:detail',
            kwargs={'pk': self.object.pk},
        )