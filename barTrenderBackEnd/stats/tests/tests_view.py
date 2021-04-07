from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Owner
from rest_framework.response import Response
from django.conf import settings
import json
from stats.views import RankingStats
from authentication.views import *
from establishments.views import Establishments
from stats.models import Ranking


class StatsViewTest(TestCase):

    def setUp(self):

        self.factory = RequestFactory()

        # Owners
        self.owner_user_one = User.objects.create_user(username='owner1@gmail.com', password="vekto1234")
        self.owner_one = Owner.objects.create(phone="111111111", user=self.owner_user_one)

    def login(self, username):
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email": username , "password":"vekto1234"})

        resp = login.post(self, request)

        return resp.data["token"]

    def test_empty_ranking(self):

        token = self.login(self.owner_one.user.username)
        request = self.factory.get("/get")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filter": "Bebida"}')
        resp = RankingStats.post(self, request)

        self.assertEqual(resp.status_code, 200)


    def test_create_ranking_no_previous(self):
        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Paulaner"]}}')

        previous_count = Ranking.objects.count()
        resp = Establishments.post(self, request)
        after_count = Ranking.objects.count()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_count - previous_count, 1)

    def test_create_ranking_previous(self):
        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Paulaner"]}}')

        previous_count = Ranking.objects.count()
        resp = Establishments.post(self, request)
        after_count_1 = Ranking.objects.count()

        resp = Establishments.post(self, request)
        after_count_2 = Ranking.objects.count()

        ranking = Ranking.objects.filter(search_date=datetime.datetime.now(), filter_enum="Bebida", type_text="Paulaner").get()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_count_1 - previous_count, 1)
        self.assertEqual(after_count_2 - after_count_1, 0)
        self.assertEqual(ranking.value_number, 2)