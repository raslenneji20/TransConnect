import uuid

from django.db import models
from EntreprisesApp.models import Entreprise
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.
class Expedition(models.Model):
    reference=models.CharField(unique=True,default=f"EXP-{uuid.uuid4().hex[:8].upper()}",editable=False)
    ville_depart=models.CharField()
    ville_arrive=models.CharField()
    poids_kg=models.DecimalField()
    datesouhaitee=models.DateField()
    desription=models.TextField()
    statut = models.CharField(
    max_length=20,
    choices=[
        ('publiee', 'Publiée'),
        ('attribuee', 'Attribuée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ],
    default='publiee')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    entreprise=models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='expeditions')
    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError("L'entreprise associée à l'expédition doit être de type 'chargeur'.")
        if self.ville_depart == self.ville_arrive:
            raise ValidationError("La ville de départ et la ville d'arrivée ne peuvent pas être identiques.")
    @classmethod
    def _generate_reference(cls):
        annee=timezone.now().strftime("%Y") 
        dernier=cls.objects.filter(reference__startswith=f"EXP-{annee}").order_by('-created_at').first()
        if dernier:
            compteur=int(dernier.reference.split('-')[-1])+1
        else:
            compteur=1
        return f"EXP-{annee}-{compteur:04d}"
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)