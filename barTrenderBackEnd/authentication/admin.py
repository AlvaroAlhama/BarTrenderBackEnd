from django.contrib import admin
from authentication.models import Owner, Client

admin.site.register(Owner)
admin.site.register(Client)