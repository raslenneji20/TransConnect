import uuid

from django.db import models
from EntreprisesApp.models import Entreprise

# Create your models here.
class Expedition(models.Model):
    reference=models.CharField(unique=True,default=f"EXP-{uuid.uuid4().hex[:8].upper()}")
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