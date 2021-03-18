from django.urls import path, include
from .views import getEstablishments

urlpatterns = [
    path('establishments', getEstablishments.as_view()),
]