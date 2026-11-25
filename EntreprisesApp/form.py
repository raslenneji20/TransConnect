from .models import Entreprise
from django import forms
class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['raison_sociale', 'matricule_fiscale', 'adresse', 'type_entreprise', 'gerant']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 4}),
        }


class EntrepriseUpdateForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['raison_sociale', 'matricule_fiscale', 'adresse']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 4}),
        }