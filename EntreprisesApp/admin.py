from django.contrib import admin
from EntreprisesApp.models import Entreprise, Utilisateur

admin.site.site_header = "TransConnect Administration"
admin.site.site_title = "TransConnect"


class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscale', 'adresse', 'type_entreprise')
    list_filter = ('type_entreprise',)
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('raison_sociale', 'matricule_fiscale', 'adresse')
    fieldsets = (
        ("Entreprise", {
            'fields': ("raison_sociale", "matricule_fiscale", "adresse", "type_entreprise")
        }),
        ("Horodatage", {
            'fields': ("created_at", "updated_at"),
            'classes': ('collapse',),
        }),
    )


class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'role', 'telephone', 'created_at', 'updated_at')
    list_filter = ('role', 'is_active')
    readonly_fields = ('user_id', 'date_joined', 'last_login', 'created_at', 'updated_at')
    search_fields = ('user_id', 'email', 'username', 'role')
    fieldsets = (
        ("Utilisateur", {
            'fields': ("user_id", "username", "email", "role", "telephone")
        }),
        ("Horodatage", {
            'fields': ("date_joined", "last_login", "created_at", "updated_at"),
            'classes': ('collapse',),
        }),
    )


admin.site.register(Entreprise, EntrepriseAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)