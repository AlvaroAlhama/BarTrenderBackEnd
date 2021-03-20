from django.contrib import admin
from authentication.models import Owner, Client, Establishment, Tag

admin.site.register(Owner)
admin.site.register(Client)
admin.site.register(Establishment)
admin.site.register(Tag)