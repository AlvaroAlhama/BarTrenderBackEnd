from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Owner
from rest_framework.response import Response
from django.conf import settings
import json
from ..models import Counter
from ..views import RankingStats
from authentication.views import *


class StatsUnitTest(TestCase):

    def setUp(self):

        self.factory = RequestFactory()

        # Owners
        self.owner_user_one = User.objects.create_user(username='owner1@gmail.com', password="vekto1234")
        self.owner_one = Owner.objects.create(phone="111111111", user=self.owner_user_one)

    def login(self, username):
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"email":"' + username + '", "password":"vekto1234"}')

        resp = login.post(self, request)

        return resp.data["token"]

    def test_empty_ranking(self):

        token = self.login(self.owner_one.user.username)
        request = self.factory.get("/get")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filter": "Bebida"}')
        resp = RankingStats.post(self, request)

        self.assertEqual(resp.status_code, 200)
