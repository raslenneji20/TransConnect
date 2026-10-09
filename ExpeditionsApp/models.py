from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from EntreprisesApp.models import Entreprise


class Expedition(models.Model):
    reference = models.CharField(max_length=13, unique=True, editable=False)  # EXP-AA-NNNNN = 12 chars, 13 for safety
    ville_depart = models.CharField(max_length=100)
    ville_arrive = models.CharField(max_length=100)
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date_souhaitee = models.DateField()
    description = models.TextField()
    statut = models.CharField(
        max_length=20,
        choices=[
            ('publiee', 'Publiée'),
            ('attribuee', 'Attribuée'),
            ('en_cours', 'En cours'),
            ('livree', 'Livrée'),
            ('annulee', 'Annulée'),
        ],
        default='publiee',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entreprise = models.ForeignKey(
        Entreprise, on_delete=models.CASCADE, related_name='expeditions'
    )

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError(
                "L'entreprise associée à l'expédition doit être de type 'chargeur'."
            )
        if self.ville_depart and self.ville_arrive and self.ville_depart == self.ville_arrive:
            raise ValidationError(
                "La ville de départ et la ville d'arrivée ne peuvent pas être identiques."
            )

    @classmethod
    def _generate_reference(cls):
        annee = timezone.now().strftime("%y")  # 2 digits, e.g. "26"
        prefix = f"EXP-{annee}-"
        # Get the highest counter for this year
        last = (
            cls.objects
            .filter(reference__startswith=prefix)
            .order_by('-reference')
            .values_list('reference', flat=True)
            .first()
        )
        if last:
            try:
                compteur = int(last.split('-')[-1]) + 1
            except (ValueError, IndexError):
                compteur = 1
        else:
            compteur = 1
        return f"{prefix}{compteur:05d}"  

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()   # optional but recommended
        super().save(*args, **kwargs)