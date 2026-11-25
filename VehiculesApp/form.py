from VehiculesApp.models import Vehicule
from django import forms
from EntreprisesApp.models import Utilisateur
from EntreprisesApp.permissions import get_user_company


class VehiculeForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None or user.is_platform_admin:
            return

        company = get_user_company(user)
        if (
            user.role != Utilisateur.Role.GERANT
            or company is None
            or company.type_entreprise != 'transporteur'
        ):
            self.fields['entreprise'].queryset = self.fields['entreprise'].queryset.none()
            return

        self.fields['entreprise'].queryset = self.fields['entreprise'].queryset.filter(
            pk=company.pk,
        )
        self.fields['entreprise'].initial = company.pk
        self.fields['entreprise'].disabled = True

    class Meta:
        model = Vehicule
        fields = ['immatriculation', 'capacite_kg', 'type_vehicule','entreprise']
    widgets = {
            'type_vehicule': forms.Select(choices=Vehicule.CAPACITE_MAX.keys()),
        }