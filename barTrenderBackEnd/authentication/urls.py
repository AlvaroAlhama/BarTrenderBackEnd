from django.urls import path, include
from .views import login, signup, SetPremium, UserInformation


urlpatterns = [
    path('login', login.as_view()),
    path('signup', signup.as_view()),
    path('setpremium', SetPremium.as_view()),
    path('user', UserInformation.as_view()),
    path('user/edit', UserInformation.as_view())
]
