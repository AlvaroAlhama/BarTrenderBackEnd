from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Client, Owner
from rest_framework.response import Response
from django.conf import settings
import authentication.utils as utils
import datetime
import pytz, json
from establishments.models import Establishment, Tag, Discount
from establishments.views import Establishments


class EstablshimentUnitTest(TestCase):
    
    def setUp(self):
        # Users
        self.client_user = User.objects.create_user('client@gmail.com')
        self.owner_user = User.objects.create_user('owner@gmail.com')
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner = Owner.objects.create(phone="123456789", user=self.owner_user)

        self.factory = RequestFactory()

        # Tags
        self.tag1 = Tag.objects.create(name='Cruzcampo', type='Bebida')
        self.tag2 = Tag.objects.create(name='Billar', type='Ocio')

        tags = [self.tag1, self.tag2]

        # Establishments
        self.establisment1 = Establishment.objects.create(
            name_text="Bar Ejemplo Uno",
            cif_text="B56316524",
            phone_number="123456789",
            zone_enum="Alameda",
            verified_bool=True,
            owner=self.owner
        )
        self.establisment1.tags.set(tags)

        self.establisment2 = Establishment.objects.create(
            name_text="Bar Ejemplo Dos",
            cif_text="G20414124",
            phone_number="123456788",
            zone_enum="Triana",
            verified_bool=True,
            owner=self.owner
        )

        # Discount
        self.discount = Discount.objects.create(
            name_text='Descuento Uno', 
            description_text='Descripción Uno', 
            cost_number=0.5, 
            totalCodes_number=100, 
            scannedCodes_number=0, 
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(milliseconds=1), 
            establishment_id=self.establisment1)

    def test_filter_all_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"beers": ["Cruzcampo"], "leisures": ["Billar"], "zones": ["Alameda"], "discounts": true}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 2)

    def test_filter_empty_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 2)
        self.assertEqual(resp.data[1]['name'], 'Bar Ejemplo Dos')
        self.assertEqual(resp.data[1]['phone'], 123456788)
        self.assertEqual(resp.data[1]['zone'], 'Triana')
        self.assertEqual(len(resp.data[1]['tags']), 0)

    def test_filter_wrong_payload(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 401)

    def test_filter_without_api(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 401)

    def test_filter_without_beer_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"leisures": ["Billar"], "zones": ["Alameda"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 2)

    def test_filter_without_leisures_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"beers": ["Cruzcampo"], "zones": ["Alameda"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 2)

    def test_filter_without_zones_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"leisures": ["Billar"], "beers": ["Cruzcampo"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 2)

    def test_filter_without_discounts_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"beers": ["Cruzcampo"], "leisures": ["Billar"], "zones": ["Alameda"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 2)

    def test_filter_beers_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"beers": ["Paulaner"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_filter_leisures_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"leisures": ["Dardos"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_filter_zones_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"zones": ["Reina Mercedes"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)