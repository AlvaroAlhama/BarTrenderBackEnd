from django.urls import path,include
from .views import *

urlpatterns = [
    path('get', RankingStats.as_view()),
    path('getPremium', RankingStatsPremium.as_view()), 
]