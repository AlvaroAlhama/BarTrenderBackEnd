from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
]

for module in settings.MODULES:
    urlpatterns += [
        path('v1/{}/'.format(module), include('{}.urls'.format(module)))
    ]