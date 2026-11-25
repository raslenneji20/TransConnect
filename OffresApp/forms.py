from django import forms

from EntreprisesApp.models import Utilisateur
from EntreprisesApp.permissions import get_user_company
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule
from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = [
            'expedition',
            'entreprise',
            'vehicule',
            'prix',
            'delai_jours',
            'date_proposition',
        ]
        widgets = {
            'date_proposition': forms.DateInput(attrs={'type': 'date'}),
        }

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
            for name in ('expedition', 'entreprise', 'vehicule'):
                self.fields[name].queryset = self.fields[name].queryset.none()
            return

        self.fields['entreprise'].queryset = self.fields['entreprise'].queryset.filter(
            pk=company.pk,
        )
        self.fields['entreprise'].initial = company.pk
        self.fields['entreprise'].disabled = True
        self.fields['expedition'].queryset = Expedition.objects.filter(
            statut='publiee',
        )
        self.fields['vehicule'].queryset = Vehicule.objects.filter(
            entreprise=company,
            disponible=True,
        )
