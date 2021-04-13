from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Owner
from rest_framework.response import Response
from django.conf import settings
import json
from stats.views import RankingStats, RankingStatsPremium
from authentication.views import *
from establishments.views import *
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
        resp = FilterEstablishments.post(self, request)
        after_count = Ranking.objects.count()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_count - previous_count, 1)

    def test_create_ranking_previous(self):
        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Paulaner"]}}')

        previous_count = Ranking.objects.count()
        resp = FilterEstablishments.post(self, request)
        after_count_1 = Ranking.objects.count()

        resp = FilterEstablishments.post(self, request)
        after_count_2 = Ranking.objects.count()

        ranking = Ranking.objects.filter(search_date=datetime.datetime.now(), filter_enum="Bebida", type_text="Paulaner").get()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(after_count_1 - previous_count, 1)
        self.assertEqual(after_count_2 - after_count_1, 0)
        self.assertEqual(ranking.value_number, 2)


class StatsPremiumViewTest(TestCase):

    def setUp(self):

        self.factory = RequestFactory()

        # Owners
        self.owner_user_one = User.objects.create_user(username='owner1@gmail.com', password="vekto1234")
        self.owner_one = Owner.objects.create(phone="111111111", user=self.owner_user_one, premium=True, premium_end_date=datetime.date.today() + datetime.timedelta(days=1))

        self.owner_user_two = User.objects.create_user(username='owner2@gmail.com', password="vekto1234")
        self.owner_two = Owner.objects.create(phone="111111112", user=self.owner_user_two)

        Ranking.objects.create(search_date=datetime.date.today(), filter_enum="Bebida", type_text="Cruzcampo", value_number=3, zone_enum="Remedios")
        Ranking.objects.create(search_date=datetime.date.today(), filter_enum="Bebida", type_text="Paulaner", value_number=2, zone_enum="Remedios")
        Ranking.objects.create(search_date=datetime.date.today() - datetime.timedelta(days=32), filter_enum="Bebida", type_text="Estrella del Sur", value_number=7, zone_enum="Remedios")

    def login(self, username):
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email": username , "password":"vekto1234"})

        resp = login.post(self, request)

        return resp.data["token"]

    def test_stats_premium_ok(self):
        token = self.login(self.owner_user_one.username)
        request = self.factory.post("/stats/getPremium")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"initial_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)),\
            "end_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1)), "filter": "Bebida", "zone": "Remedios"}

        response = RankingStatsPremium.post(self, request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first']['name'], 'Cruzcampo')
        self.assertEqual(response.data['first']['real'], 3)
        self.assertEqual(response.data['first']['percentage'], 60.0)

    def test_stats_no_premium_fail(self):
        token = self.login(self.owner_user_two.username)
        request = self.factory.post("/stats/getPremium")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"initial_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)),\
            "end_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1)), "filter": "Bebida", "zone": "Remedios"}

        response = RankingStatsPremium.post(self, request)

        self.assertEqual(response.status_code, 401)
        self.assertTrue('A017' in str(response.data['error']))

    def test_stats_premium_data_wrong_fail(self):
        token = self.login(self.owner_user_one.username)
        request = self.factory.post("/stats/getPremium")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"initial_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)),\
            "end_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1)), "zone": "Remedios"}

        response = RankingStatsPremium.post(self, request)

        self.assertEqual(response.status_code, 400)
        self.assertTrue('Z001' in str(response.data['error']))

    def test_stats_premium_past_ok(self):
        token = self.login(self.owner_user_one.username)
        request = self.factory.post("/stats/getPremium")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"initial_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) - datetime.timedelta(days=33)),\
            "end_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) - datetime.timedelta(days=2)), "filter": "Bebida", "zone": "Remedios"}

        response = RankingStatsPremium.post(self, request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first']['name'], 'Estrella del Sur')
        self.assertEqual(response.data['first']['real'], 7)
        self.assertEqual(response.data['first']['percentage'], 100.0)

    def test_stats_premium_empty_zone_ok(self):
        token = self.login(self.owner_user_one.username)
        request = self.factory.post("/stats/getPremium")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"initial_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)),\
            "end_date": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1)), "filter": "Bebida", "zone": "Triana"}

        response = RankingStatsPremium.post(self, request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first']['name'], 'None')
        self.assertEqual(response.data['first']['real'], 0)
        self.assertEqual(response.data['first']['percentage'], 0.0)
