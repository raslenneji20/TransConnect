from VehiculesApp.models import Vehicule
from django import forms
class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['immatriculation', 'capacite_kg', 'type_vehicule','entreprise']
    widgets = {
            'type_vehicule': forms.Select(choices=Vehicule.CAPACITE_MAX.keys()),
        }