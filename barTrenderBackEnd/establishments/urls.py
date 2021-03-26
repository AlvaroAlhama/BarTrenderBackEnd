from django.urls import path,include
from .views import *

urlpatterns = [
    # Get Discount from establishment
    path('<int:establishment_id>/discounts/get', Discounts.as_view()),
    # Get QR
    path('<int:establishment_id>/discounts/<int:discount_id>/getQR', DiscountsQR.as_view()),
    # Get Establishments
    path('get', Establishments.as_view()),
    # Scan Code
    path('<int:establishment_id>/discounts/<int:discount_id>/scan', ScanDiscount.as_view()),
    #Create Discount
    path('<int:establishment_id>/discounts/create', Discounts.as_view()),
    # Scan Code
    path('<int:establishment_id>/discounts/<int:discount_id>/update', Discounts.as_view())
]
