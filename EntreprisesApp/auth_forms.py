from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Entreprise, Utilisateur


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=(
            (Utilisateur.Role.GERANT, 'Gérant'),
            (Utilisateur.Role.CHARGEUR, 'Chargeur'),
        ),
        label='Type de compte',
    )
    raison_sociale = forms.CharField(max_length=200, label='Nom de l’entreprise')
    matricule_fiscale = forms.CharField(
        max_length=17,
        validators=Entreprise._meta.get_field('matricule_fiscale').validators,
        label='Matricule fiscale',
    )
    adresse = forms.CharField(
        validators=Entreprise._meta.get_field('adresse').validators,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Adresse de l’entreprise',
    )

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ('username', 'email', 'telephone', 'role')
        labels = {
            'username': 'Nom d’utilisateur',
            'email': 'Adresse e-mail',
            'telephone': 'Téléphone',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemple@gmail.com',
                'inputmode': 'email',
            }),
            'telephone': forms.TextInput(attrs={
                'pattern': '[0-9]+',
                'inputmode': 'numeric',
                'placeholder': '20123456',
            }),
        }

    def clean_matricule_fiscale(self):
        value = self.cleaned_data['matricule_fiscale']
        if Entreprise.objects.filter(matricule_fiscale=value).exists():
            raise ValidationError('Ce matricule fiscal est déjà utilisé.')
        return value

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telephone = self.cleaned_data['telephone']
        user.role = self.cleaned_data['role']

        if commit:
            with transaction.atomic():
                user.save()
                company_type = (
                    'transporteur'
                    if user.role == Utilisateur.Role.GERANT
                    else 'chargeur'
                )
                Entreprise.objects.create(
                    raison_sociale=self.cleaned_data['raison_sociale'],
                    matricule_fiscale=self.cleaned_data['matricule_fiscale'],
                    adresse=self.cleaned_data['adresse'],
                    type_entreprise=company_type,
                    gerant=user,
                )
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'telephone')
        labels = {
            'username': 'Nom d’utilisateur',
            'email': 'Adresse e-mail',
            'telephone': 'Téléphone',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemple@gmail.com',
                'inputmode': 'email',
            }),
            'telephone': forms.TextInput(attrs={
                'pattern': '[0-9]+',
                'inputmode': 'numeric',
                'placeholder': '20123456',
            }),
        }


class DeactivateAccountForm(forms.Form):
    password = forms.CharField(
        label='Mot de passe actuel',
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise ValidationError('Le mot de passe est incorrect.')
        return password
