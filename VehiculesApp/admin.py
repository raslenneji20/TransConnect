from django.contrib import admin
from VehiculesApp.models import Vehicule
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'capacite_kg', 'type_vehicule','dispoendnible','entreprise','created_at','updated_at')

admin.site.register(Vehicule, VehiculeAdmin)
# Register your models here.
