from django.contrib import admin
from OffresApp.models import Offre

class OffreAdmin(admin.ModelAdmin):
    list_display = ('prix','delai_jours','statut','expedition','entreprise','vehicule')
    list_filter = ('statut', 'entreprise', 'vehicule')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('prix', 'delai_jours', 'statut', 'expedition__reference', 'entreprise__raison_sociale', 'vehicule__immatriculation')
admin.site.register(Offre, OffreAdmin)
# Register your models here.
