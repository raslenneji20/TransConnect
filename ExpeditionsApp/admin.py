from django.contrib import admin
from ExpeditionsApp.models import Expedition
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrive', 'poids_kg', 'date_souhaitee', 'statut')
admin.site.register(Expedition, ExpeditionAdmin)