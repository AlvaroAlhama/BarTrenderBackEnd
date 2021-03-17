from django.urls import path, include
from .views import *

urlpatterns = [
    path('get/<slug:token>/<int:establishment_id>/<int:discount_id>', Discounts.as_view()),
]
