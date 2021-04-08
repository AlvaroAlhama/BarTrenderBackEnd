from django.urls import path,include
from .views import *

urlpatterns = [
    path("establishments/<int:establishment_id>/calculate", CalculatePayment.as_view())
]