from django.contrib import admin
from django.utils import timezone
from ExpeditionsApp.models import Expedition
class EnRetardFilter(admin.SimpleListFilter):
    title = 'En retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return (
            ('oui', 'Oui'),
            ('non', 'Non'),
        )

    def queryset(self, request, queryset):
        aujourd_hui = timezone.now().date()    
        if self.value() == 'oui':
            return queryset.filter(date_souhaitee__lt=aujourd_hui, statut='publie')
        elif self.value() == 'non':
           return queryset.exclude(date_souhaitee__lt=aujourd_hui, statut='publie')
        return queryset
@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrive', 'poids_kg', 'date_souhaitee', 'statut')
    list_filter = ('statut', 'date_souhaitee', 'entreprise', EnRetardFilter)
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
