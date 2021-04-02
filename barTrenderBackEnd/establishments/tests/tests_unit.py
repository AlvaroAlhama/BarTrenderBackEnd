from rest_framework.test import APIClient
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Client, Owner
from rest_framework.response import Response
from django.conf import settings
import datetime
import pytz, json
from establishments.models import Establishment, Tag, Discount
from establishments.views import Establishments, ScanDiscount
from authentication.views import *
import establishments.utils as utils


class ScanQRUnitTest(TestCase):

    def setUp(self):

        self.factory = RequestFactory()

        # Owners
        self.owner_user_one = User.objects.create_user(username='owner1@gmail.com', password="vekto1234")
        self.owner_one = Owner.objects.create(phone="111111111", user=self.owner_user_one)

        self.owner_user_two = User.objects.create_user('owner2@gmail.com')
        self.owner_two = Owner.objects.create(phone="222222222", user=self.owner_user_two)

        self.owner_user_three = User.objects.create_user('owner3@gmail.com', password="vekto1234")
        self.owner_three = Owner.objects.create(phone="333333333", user=self.owner_user_three)

        # Clients
        self.client_user_one = User.objects.create_user(username='client1@gmail.com', password="vekto1234")
        self.client = Client.objects.create(birthday=datetime.datetime.now(), user=self.client_user_one)

        # Establishments
        # Establishment of owner_one

        self.establishment_one = Establishment.objects.create(
            name_text="Bar Ejemplo Uno",
            cif_text="B56316524",
            phone_number="123456789",
            zone_enum="Alameda",
            verified_bool=True,
            owner=self.owner_one
        )

        self.establishment_two = Establishment.objects.create(
            name_text="Bar Ejemplo Dos",
            cif_text="G20414124",
            phone_number="123456788",
            zone_enum="Triana",
            verified_bool=True,
            owner=self.owner_two
        )

        # Discounts
        # Valid Discount Establishment One
        self.discount_one = Discount.objects.create(
            name_text='Descuento Uno',
            description_text='Descripción Uno',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=0,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            establishment_id=self.establishment_one)

        self.discount_one.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount_one.update()

        # Valid Discount Establishment Two
        self.discount_two = Discount.objects.create(
            name_text='Descuento Dos',
            description_text='Descripción Dos',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=0,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            establishment_id=self.establishment_two)
        self.discount_two.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount_two.update()

        # Valid Discounts but invalid for Scan
        self.discount_invalid_future = Discount.objects.create(
            name_text='Descuento Uno',
            description_text='Descripción Uno',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=0,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            establishment_id=self.establishment_one)

        self.discount_invalid_expired = Discount.objects.create(
            name_text='Descuento Uno',
            description_text='Descripción Uno',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=0,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            end_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=2),
            establishment_id=self.establishment_one)

        self.discount_invalid_expired.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=2)
        self.discount_invalid_expired.end_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount_invalid_expired.update()

        self.discount_invalid_all_scanned = Discount.objects.create(
            name_text='Descuento Uno',
            description_text='Descripción Uno',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=100,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            establishment_id=self.establishment_one)

        self.discount_invalid_all_scanned.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount_invalid_all_scanned.update()

        self.discount_invalid_client_already_scanned = Discount.objects.create(
            name_text='Descuento Uno',
            description_text='Descripción Uno',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=0,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            establishment_id=self.establishment_one)

        self.discount_invalid_client_already_scanned.clients_id.add(self.client)

        self.discount_invalid_client_already_scanned.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount_invalid_client_already_scanned.update()

    def login(self, username):
        api_call = "/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}

        body = {
            "email": username,
            "password": "vekto1234"
        }
        request._body = json.dumps(body)

        resp = login.post(self, request)
        return resp.data["token"]

    def test_valid_scan_qr(self):

        token = self.login(self.owner_one.user.username)
        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_one.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(prev_scanned_codes + 1, after_scanned_codes)
        self.assertEqual(resp.data["msg"], "Success Scanning the QR. Discount applied!")

    def test_invalid_scan_qr_owner_not_exist(self):
        token = self.login(self.owner_three.user.username)
        self.owner_three.delete()

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_one.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(prev_scanned_codes, after_scanned_codes)
        self.assertEqual(resp.data["error"], "A002: Owner no existe")

    def test_invalid_scan_qr_establishment_not_from_owner(self):
        token = self.login(self.owner_one.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_two.id,
            'discount_id': self.discount_two.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_scanned_codes, after_scanned_codes)
        self.assertEqual(resp.data["error"], "E002: El establecimiento no pertenece al dueño")

    def test_invalid_scan_qr_invalid_discount(self):
        token = self.login(self.owner_one.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_two.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_scanned_codes, after_scanned_codes)
        self.assertEqual(resp.data["error"], "D002: Descuento no pertenece al establecimiento")

    def test_invalid_scan_qr_discount_initial_date_future(self):

        token = self.login(self.owner_one.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_future.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_scanned_codes, after_scanned_codes)
        self.assertEqual(resp.data["error"], "D021: El descuento aun no ha comenzado")

    def test_invalid_scan_qr_discount_expired(self):

        token = self.login(self.owner_one.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_expired.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_scanned_codes, after_scanned_codes)
        self.assertEqual(resp.data["error"], "D003: El descuento ha expirado")

    def test_invalid_scan_qr_discount_all_scanned(self):
        token = self.login(self.owner_one.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_all_scanned.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_scanned_codes, after_scanned_codes)
        self.assertEqual(resp.data["error"], "D004: No quedan descuentos disponibles")

    def test_invalid_scan_qr_discount_client_all_scanned(self):
        token = self.login(self.owner_one.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/client/<int:client_id>/scan")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_client_already_scanned.id,
            'client_id': self.client.id
        }

        prev_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number
        resp = ScanDiscount.get(self, request, **url_data)
        after_scanned_codes = Discount.objects.get(id=self.discount_one.id).scannedCodes_number

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_scanned_codes, after_scanned_codes)
        self.assertEqual(resp.data["error"], "D005: Descuento ya escaneado por usuario")


class EstablishmentUnitTest(TestCase):
    
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
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=1),
            establishment_id=self.establisment1)

        self.discount.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount.update()

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

class DiscountViewTest(TestCase):
    
    def setUp(self):
        # Users
        self.client_user = User.objects.create_user('client@gmail.com')
        self.owner_user = User.objects.create_user('owner@gmail.com')
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner = Owner.objects.create(phone="123456789", user=self.owner_user)

        self.factory = RequestFactory()

        # Establishments
        self.establisment1 = Establishment.objects.create(
            name_text="Bar Ejemplo Uno",
            cif_text="B56316524",
            phone_number="123456789",
            zone_enum="Alameda",
            verified_bool=True,
            owner=self.owner
        )

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
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=1),
            establishment_id=self.establisment1)

        self.discount.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount.update()

    
