from django.urls import path, include
from .views import login, testAll, testOwner


urlpatterns = [
    path('login', login.as_view()),
    path('test/all', testAll.as_view()),
    path('test/owner', testOwner.as_view())
]
