from django.urls import path,include
from .views import *

urlpatterns = [
    path('<int:establishment_id>/discounts/get/', Discounts.as_view()),
    path('<int:establishment_id>/discounts/<int:discount_id>/getQR/', DiscountsQR.as_view()),
]
