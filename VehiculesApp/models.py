from django.db import models

# Create your models here.
class vehicule(models.Model):
    immatriculation=models.CharField(unique=True)
    capacite_kg=models.PositiveIntegerField()
    type_vehicule = models.CharField(
    max_length=20,
    choices=[
        ('camion', 'Camion'),
        ('remorque', 'Remorque'),
        ('fourgon', 'Fourgon'),
    ],
    default='camion'
)
    disponible=models.BooleanField(default=True)
    entreprise=models.ForeignKey('EntreprisesApp.Entreprise', on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    