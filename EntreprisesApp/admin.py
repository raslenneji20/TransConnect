from django.contrib import admin

import EntreprisesApp
from ExpeditionsApp.models import Expedition
from OffresApp.models import offre
from VehiculesApp.models import vehicule
from .models import *

admin.site.register(Entreprise)
admin.site.register(Utilisateur)
admin.site.register(Expedition)
admin.site.register(vehicule)
admin.site.register(offre)
# Register your models here.
