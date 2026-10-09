import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Validators / helpers
# ---------------------------------------------------------------------------

def email_validator(value):
    if not value.endswith('@gmail.com'):
        raise ValidationError("L'adresse e-mail doit se terminer par '@gmail.com'.")
    return value


from django.utils import timezone

def generate_user_id():
    annee = timezone.now().strftime("%y")           
    prefix = f"{annee}user"
    # Find the last ID with this prefix and increment
    last = (
        Utilisateur.objects
        .filter(user_id__startswith=prefix)
        .order_by('-user_id')
        .values_list('user_id', flat=True)
        .first()
    )
    if last:
        try:
            n = int(last[-2:]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    if n > 99:
        raise ValueError("Limite annuelle de 99 utilisateurs atteinte.")
    return f"{prefix}{n:02d}"


matricule_fiscale_validator = RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdenpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message="Le format du matricule fiscale est invalide. Il doit être au format 1234567/A/B/C/123."
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Utilisateur(AbstractUser):
    user_id = models.CharField(
        max_length=8,
        primary_key=True,
        default=generate_user_id,
        editable=False,
    )
    email = models.EmailField(unique=True, validators=[email_validator])
    telephone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["email", "role"]

    def __str__(self):
        return f"{self.username} ({self.user_id})"


class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200)
    matricule_fiscale = models.CharField(
        max_length=17,
        unique=True,
        validators=[matricule_fiscale_validator],
    )
    adresse = models.TextField(
        validators=[MinLengthValidator(20, "La longueur doit être supérieure à 20 caractères.")]
    )
    type_entreprise = models.CharField(
        max_length=100,
        choices=[
            ('chargeur', 'Chargeur'),
            ('transporteur', 'Transporteur'),
        ],
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    gerant = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='entreprise',
    )

    def __str__(self):
        return self.raison_sociale
    