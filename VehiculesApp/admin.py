from django.contrib import admin
from VehiculesApp.models import Vehicule
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'capacite_kg', 'type_vehicule','disponible','entreprise','created_at','updated_at')
    list_filter = ('type_vehicule', 'disponible', 'entreprise')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('immatriculation', 'type_vehicule', 'entreprise__raison_sociale')
    fieldsets = (
        ("Véhicule", {
            'fields': ("immatriculation", "type_vehicule","capacite_kg","disponible")
        }),
        ("Entreprise", {
            'fields': ("entreprise",),
        }),
        ("Horodatage", {
            'fields': ("created_at", "updated_at"),
            'classes': ('collapse',),
        }),
    )
admin.site.register(Vehicule, VehiculeAdmin)
# Register your models here.
 