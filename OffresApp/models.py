from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule


class Offre(models.Model):
    prix = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(
        max_length=20,
        choices=[
            ('proposee', 'Proposée'),
            ('acceptee', 'Acceptée'),
            ('refusee', 'Refusée'),
            ('retiree', 'Retirée'),
        ],
        default='proposee',
    )
    date_proposition = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    expedition = models.ForeignKey(
        Expedition, on_delete=models.CASCADE, related_name='offres'
    )
    entreprise = models.ForeignKey(
        Entreprise, on_delete=models.CASCADE, related_name='offres'
    )
    vehicule = models.ForeignKey(
        Vehicule, on_delete=models.CASCADE, related_name='offres'
    )

    class Meta:
        constraints = [
            # Rule 4 — DB-level: one active "proposee" offer per (expedition, entreprise)
            models.UniqueConstraint(
                fields=['expedition', 'entreprise'],
                condition=models.Q(statut='proposee'),
                name='unique_offre_proposee_par_entreprise_expedition',
            ),
        ]

    def clean(self):
        super().clean()

        # Rule 1 — the offering company must be a transporteur
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({
                'entreprise': "L'entreprise qui fait une offre doit être de type 'transporteur'."
            })

        # Rule 2 — the vehicle must belong to the offering company
        if self.vehicule_id and self.entreprise_id:
            if self.vehicule.entreprise_id != self.entreprise_id:
                raise ValidationError({
                    'vehicule': "Le véhicule proposé doit appartenir à l'entreprise qui fait l'offre."
                })

        # Rule 6 — the vehicle must be available
        if self.vehicule_id and not self.vehicule.disponible:
            raise ValidationError({
                'vehicule': "Ce véhicule n'est pas disponible."
            })

        # Rule 3 — the expedition must be 'publiee' to receive new offers
        if self.expedition_id and self.expedition.statut != 'publiee':
            raise ValidationError({
                'expedition': "Cette expédition n'accepte plus de nouvelles offres."
            })

        # Rule 4 — no two active "proposee" offers per (expedition, entreprise)
        if self.expedition_id and self.entreprise_id and self.statut == 'proposee':
            qs = Offre.objects.filter(
                expedition_id=self.expedition_id,
                entreprise_id=self.entreprise_id,
                statut='proposee',
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    "Cette entreprise a déjà une offre active sur cette expédition."
                )

        # Rule 7 — vehicle type must be compatible with the expedition weight
        if self.vehicule_id and self.expedition_id:
            max_kg = Vehicule.CAPACITE_MAX.get(self.vehicule.type_vehicule)
            if max_kg is None:
                raise ValidationError({'vehicule': "Type de véhicule inconnu."})
            if float(self.expedition.poids_kg) > max_kg:
                raise ValidationError({
                    'vehicule': (
                        f"Ce véhicule ({self.vehicule.get_type_vehicule_display()}) "
                        f"ne supporte que {max_kg} kg, "
                        f"or l'expédition pèse {self.expedition.poids_kg} kg."
                    )
                })
        if self.vehicule_id and not self.vehicule.disponible:
            raise ValidationError({'vehicule': "Ce véhicule n'est pas disponible."})
        if self.vehicule_id and self.expedition_id:
            max_kg = Vehicule.CAPACITE_MAX.get(self.vehicule.type_vehicule)
            if max_kg is None:
              raise ValidationError({'vehicule': "Type de véhicule inconnu."})
            if float(self.expedition.poids_kg) > max_kg:
             raise ValidationError({
            'vehicule': f"Ce véhicule ne supporte que {max_kg} kg, l'expédition pèse {self.expedition.poids_kg} kg."
        })
    def save(self, *args, **kwargs):
        self.full_clean()   # run rules even outside the admin
        super().save(*args, **kwargs)

        # Rule 5 — cascade on acceptance
        if self.statut == 'acceptee':
            self._accept_cascade()

    def _accept_cascade(self):
        # Expedition → attribuee (bypass custom save to avoid re-validation loops)
        exp = self.expedition
        if exp.statut != 'attribuee':
            exp.statut = 'attribuee'
            super(Expedition, exp).save(update_fields=['statut', 'updated_at'])

        # All other "proposee" offers on this expedition → refusee
        Offre.objects.filter(
            expedition=self.expedition, statut='proposee'
        ).exclude(pk=self.pk).update(statut='refusee')

    def __str__(self):
        return f"Offre {self.pk} - {self.prix} DT"