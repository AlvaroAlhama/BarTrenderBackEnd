from django.urls import path, include
from .views import *

urlpatterns = [
    path('test/', getTestMsg.as_view()),
]
