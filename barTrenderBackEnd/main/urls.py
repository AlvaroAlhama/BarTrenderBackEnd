from django.urls import path, include
from .views import getTestMsg

urlpatterns = [
    path('test/', getTestMsg.as_view()),
]
