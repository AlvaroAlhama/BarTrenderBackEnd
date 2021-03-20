from django.urls import path,include
from .views import *

urlpatterns = [
    path('<int:establishment_id>/discounts/<int:discount_id>/getDiscountQR', Discounts.as_view()),
]
