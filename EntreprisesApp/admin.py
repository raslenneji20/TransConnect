from django.contrib import admin

import EntreprisesApp
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule
from .models import *

admin.site.register(Entreprise)
admin.site.register(Utilisateur)
admin.site.register(Expedition)
admin.site.register(Vehicule)
admin.site.register(Offre)
# Register your models here.
