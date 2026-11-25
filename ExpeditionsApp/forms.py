from django import forms

from EntreprisesApp.models import Utilisateur
from EntreprisesApp.permissions import get_user_company
from ExpeditionsApp.models import Expedition


class ExpeditionForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None or user.is_platform_admin:
            return

        company = get_user_company(user)
        companies = self.fields['entreprise'].queryset
        if user.role == Utilisateur.Role.CHARGEUR and company is not None:
            self.fields['entreprise'].queryset = companies.filter(
                pk=company.pk,
                type_entreprise='chargeur',
            )
            self.fields['entreprise'].initial = company.pk
            self.fields['entreprise'].disabled = True
        else:
            self.fields['entreprise'].queryset = companies.none()

    class Meta:
        model = Expedition
        fields = ['ville_depart',
    'ville_arrive',
    'poids_kg',
    'date_souhaitee',  
    'description',
    'entreprise',]
        widgets = {
            'date_souhaitee': forms.DateInput(attrs={'type': 'date'}),
        }
    