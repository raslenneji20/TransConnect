from django.contrib import admin
from EntreprisesApp.models import Entreprise, Utilisateur

class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ( 'raison_sociale','matricule_fiscale','adresse','type_entreprise' )

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('user_id','email','role','telephone','created_at','updated_at')

admin.site.register(Entreprise, EntrepriseAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)
