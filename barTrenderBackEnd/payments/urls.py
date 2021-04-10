from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    # Calculate the price to pay
    path("establishments/<int:establishment_id>/calculate", CalculatePayment.as_view()),
    # Url to pay
    path("establishments/<int:establishment_id>/pay", MakePayment.as_view()),
]