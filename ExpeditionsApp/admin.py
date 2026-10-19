from django.contrib import admin
from ExpeditionsApp.models import Expedition
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrive', 'poids_kg', 'date_souhaitee', 'statut')
    list_filter = ('statut', 'date_souhaitee', 'entreprise')
    readonly_fields = ('reference', 'created_at', 'updated_at')
    search_fields = ('reference', 'ville_depart', 'ville_arrive', 'entreprise__raison_sociale')
    fieldsets = (
        ("Expédition", {
            'fields': ("reference", "entreprise","description")
        }),
        ("unitaire et poids",{"fields": ("ville_depart", "ville_arrive", "poids_kg", "date_souhaitee")}),
        ("statut et horodatage", {
            'fields': ("statut","created_at", "updated_at"),
            'classes': ('collapse',),
        }),)
admin.site.register(Expedition, ExpeditionAdmin)