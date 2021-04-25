from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
]

for module in settings.MODULES:
    urlpatterns += [
        path('v1/{}/'.format(module), include('{}.urls'.format(module))),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
