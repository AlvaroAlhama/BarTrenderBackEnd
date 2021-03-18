from django.contrib import admin
from authentication.models import Owner, Client, Establishment

admin.site.register(Owner)
admin.site.register(Client)
admin.site.register(Establishment)