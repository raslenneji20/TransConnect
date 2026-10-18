from django.contrib import admin
from OffresApp.models import Offre

class OffreAdmin(admin.ModelAdmin):
    list_display = ('prix','delai_jours','statut','expedition','entreprise','vehicule')
admin.site.register(Offre, OffreAdmin)
# Register your models here.
