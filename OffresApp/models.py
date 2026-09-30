from django.db import models
from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import vehicule
# Create your models here.
class offre(models.Model):
    prix=models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours=models.PositiveIntegerField()
    statut = models.CharField(
    max_length=20,
    choices=[
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),
    ],default='proposee')   
    date_proposition=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    expedition = models.ForeignKey(
        Expedition,
        on_delete=models.CASCADE,
        related_name='offres'
    )

    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='offres'
    )

    vehicule = models.ForeignKey(
        vehicule,
        on_delete=models.CASCADE,
        related_name='offres'
    )



