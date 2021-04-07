from rest_framework.test import APIClient
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Client, Owner
from rest_framework.response import Response
from django.conf import settings
import datetime
import pytz, json
from establishments.models import Establishment, Tag, Discount
from establishments.views import Establishments, ScanDiscount, Discounts, DiscountsQR, Establishment_By_EstablishmentId, EstablishmentsByOwner, Tags
from authentication.views import *
import establishments.utils as utils


class GetDiscountViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Owners
        self.owner_user_one = User.objects.create_user(username='owner1@gmail.com', password="vekto1234")
        self.owner_one = Owner.objects.create(phone="111111111", user=self.owner_user_one)

        self.owner_user_two = User.objects.create_user('owner2@gmail.com')
        self.owner_two = Owner.objects.create(phone="222222222", user=self.owner_user_two)

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

        self.discount_invalid_client_already_scanned.initial_date = datetime.datetime.now(
            pytz.utc) - datetime.timedelta(days=1)
        self.discount_invalid_client_already_scanned.update()

    def login(self, username):
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email": str(username), "password":"vekto1234"})

        resp = login.post(self, request)

        return resp.data["token"]

    def test_valid_get_discount(self):
        token = self.login(self.client.user.username)
        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR?custom_host=localhost:8000")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_one.id
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 200)

    def test_invalid_establishment_invalid(self):
        token = self.login(self.client.user.username)
        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': 3,
            'discount_id': self.discount_one.id
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data["error"], "E001: Establecimiento no existe")

    def test_invalid_discount_does_not_exist(self):
        token = self.login(self.client.user.username)
        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': 10
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data["error"], "D001: Descuento no existe")

    def test_invalid_discount_invalid_establishment(self):
        token = self.login(self.client.user.username)
        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_two.id,
            'discount_id': self.discount_one.id
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["error"], "D002: Descuento no pertenece al establecimiento")

    def test_invalid_discount_initial_date_future(self):
        token = self.login(self.client.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_future.id,
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["error"], "D021: El descuento aun no ha comenzado")

    def test_invalid_discount_expired(self):
        token = self.login(self.client.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_expired.id,
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["error"], "D003: El descuento ha expirado")

    def test_invalid_discount_all_scanned(self):
        token = self.login(self.client.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_all_scanned.id,
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["error"], "D004: No quedan descuentos disponibles")

    def test_invalid_discount_client_all_scanned(self):
        token = self.login(self.client.user.username)

        request = self.factory.get("<int:establishment_id>/discounts/<int:discount_id>/getQR")
        request.headers = {'token': token, 'Content-Type': 'application/json'}

        url_data = {
            'establishment_id': self.establishment_one.id,
            'discount_id': self.discount_invalid_client_already_scanned.id,
        }

        resp = DiscountsQR.get(self, request, **url_data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["error"], "D005: Descuento ya escaneado por usuario")


class ScanQRViewTest(TestCase):

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
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email": str(username), "password":"vekto1234"})

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


class EstablishmentViewTest(TestCase):
    
    def setUp(self):
        # Users
        self.client_user = User.objects.create_user(username='client@gmail.com', password="vekto1234")
        self.owner_user = User.objects.create_user(username='owner@gmail.com', password="vekto1234")
        self.owner_user_two = User.objects.create_user(username='owner2@gmail.com', password="vekto1234")
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner = Owner.objects.create(phone="123456789", user=self.owner_user)
        self.owner_two = Owner.objects.create(phone="222222222", user=self.owner_user_two)

        self.factory = RequestFactory()

        # Tags
        self.tag1 = Tag.objects.create(name='Cruzcampo', type='Bebida')
        self.tag2 = Tag.objects.create(name='Billar', type='Ocio')
        self.tag3 = Tag.objects.create(name='Arabe', type='Estilo')
        self.tag4 = Tag.objects.create(name='Joven', type='Ambiente')

        tags = [self.tag1, self.tag2, self.tag3, self.tag4]

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

    def login(self, username):
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email": str(username), "password":"vekto1234"})

        resp = login.post(self, request)

        return resp.data["token"]

    def test_filter_all_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Cruzcampo"], "Ocio": ["Billar"], "Zona": ["Alameda"], "Estilo": ["Arabe"], "Ambiente": ["Joven"], "discounts": true}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)

    def test_filter_empty_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)
        self.assertEqual(resp.data[1]['name'], 'Bar Ejemplo Dos')
        self.assertEqual(resp.data[1]['phone'], 123456788)
        self.assertEqual(resp.data[1]['zone'], 'Triana')
        self.assertEqual(len(resp.data[1]['tags']), 0)

    def test_filter_wrong_payload(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 400)

    def test_filter_without_api(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 401)

    def test_filter_without_beer_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Ocio": ["Billar"], "Zona": ["Alameda"], "Estilo": ["Arabe"], "Ambiente": ["Joven"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)

    def test_filter_without_leisures_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Cruzcampo"], "Zona": ["Alameda"], "Estilo": ["Arabe"], "Ambiente": ["Joven"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)

    def test_filter_without_zones_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Ocio": ["Billar"], "Bebida": ["Cruzcampo"], "Estilo": ["Arabe"], "Ambiente": ["Joven"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)

    def test_filter_without_discounts_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Cruzcampo"], "Ocio": ["Billar"], "Zona": ["Alameda"], "Estilo": ["Arabe"], "Ambiente": ["Joven"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)

    def test_filter_without_styles_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Cruzcampo"], "Ocio": ["Billar"], "Zona": ["Alameda"], "Ambiente": ["Joven"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)

    def test_filter_without_circles_correct(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Cruzcampo"], "Ocio": ["Billar"], "Zona": ["Alameda"], "Estilo": ["Arabe"], "discounts": false}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data[0]['phone'], 123456789)
        self.assertEqual(resp.data[0]['zone'], 'Alameda')
        self.assertEqual(len(resp.data[0]['tags']), 4)

    def test_filter_beers_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Bebida": ["Paulaner"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_filter_leisures_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Ocio": ["Dardos"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_filter_zones_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Zona": ["Reina Mercedes"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_filter_styles_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Estilo": ["Ambiente deportivo"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_filter_circles_not_match(self):

        request = self.factory.post("/establishments/get")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request.data = json.loads('{"filters": {"Ambiente": ["Viejo"]}}')
        resp = Establishments.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_get_establishment_by_establishment_id_ok(self):
        token = self.login(self.owner_user.username)
        request = self.factory.get("<int:establishment_id>/get")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id': self.establisment1.id }
        resp = Establishment_By_EstablishmentId.get(self, request, **url_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["establishment"]['name'], 'Bar Ejemplo Uno')
        self.assertEqual(resp.data["establishment"]['phone'], 123456789)
        self.assertEqual(resp.data["discounts"][0]["name"], 'Descuento Uno')
    
    def test_get_establishment_by_establishment_id_bad_id(self):
        token = self.login(self.owner_user.username)
        request = self.factory.get("<int:establishment_id>/get")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id': 52 }
        resp = Establishment_By_EstablishmentId.get(self, request, **url_data)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue("E002" in str(resp.data["error"]))

    def test_get_establishment_by_owner(self):
        token = self.login(self.owner_user.username)

        request = self.factory.get("/get_by_owner")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        resp = EstablishmentsByOwner.get(self, request)

        self.assertEqual(resp.status_code, 200)

    def test_invalid_get_establishment_by_owner_not_exists(self):
        token = self.login(self.owner_two.user.username)
        self.owner_two.delete()

        request = self.factory.get("/get_by_owner")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        resp = EstablishmentsByOwner.get(self, request)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data["error"], "A002: Owner no existe")

    def test_get_tags_correct(self):

        request = self.factory.get("/establishments/get_tags")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        resp = Tags.get(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['tags']), 6)


class DiscountViewTest(TestCase):
    
    def setUp(self):
        # Users
        self.client_user = User.objects.create_user(username='client@gmail.com', password="vekto1234")
        self.owner_user = User.objects.create_user(username='owner@gmail.com', password="vekto1234")
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner = Owner.objects.create(phone="123456789", user=self.owner_user)

        self.factory = RequestFactory()

        # Establishments
        self.establishment1 = Establishment.objects.create(
            name_text="Bar Ejemplo Uno",
            cif_text="B56316524",
            phone_number="123456789",
            zone_enum="Alameda",
            verified_bool=True,
            owner=self.owner
        )
        self.establishment2 = Establishment.objects.create(
            name_text="Bar Ejemplo Dos",
            cif_text="G20414124",
            phone_number="123456788",
            zone_enum="Triana",
            verified_bool=True,
            owner=self.owner
        )

        # Discounts
        self.discount_one = Discount.objects.create(
            name_text='Descuento Uno',
            description_text='Descripción Uno',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=20,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            establishment_id=self.establishment1)

        self.discount_one.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount_one.update()

        self.discount_two = Discount.objects.create(
            name_text='Descuento Dos',
            description_text='Descripción Dos',
            cost_number=0.5,
            totalCodes_number=100,
            scannedCodes_number=0,
            initial_date=datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1),
            establishment_id=self.establishment2)
        self.discount_two.initial_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1)
        self.discount_two.update()

    def login(self, username):
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email": str(username), "password":"vekto1234"})

        resp = login.post(self, request)

        return resp.data["token"]

    """
    def test_get_discount_ok(self):

        request = self.factory.get("<int:establishment_id>/discounts/get?all=False")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}

        url_data = { 'establishment_id': self.establishment1.id }

        resp = Discounts.get(self, request, **url_data)
        print(resp.data)
    
    """
    
    def test_create_discount_ok(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/create")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id': self.establishment1.id }
        request.data = {
            "name": "discount chupiguay",
            "description": "descripción peta",
            "cost": 0.5,
            "totalCodes": 5,
            "initialDate": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=4)),
            "endDate": 	datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=10))
        }

        prev_discounts = Discount.objects.all().count()
        resp = Discounts.post(self, request, **url_data)
        after_discounts = Discount.objects.all().count()

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(prev_discounts + 1, after_discounts)
        self.assertEqual(resp.data["msg"], "The discount has been created")

    def test_create_discount_past_initial_date_past(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/create")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id': self.establishment1.id }
        request.data = {
            "name": "discount chupiguay",
            "description": "descripción peta",
            "cost": 0.5,
            "totalCodes": 5,
            "initialDate": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) - datetime.timedelta(hours=4)),
            "endDate": 	datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=10))
        }

        prev_discounts = Discount.objects.all().count()
        resp = Discounts.post(self, request, **url_data)
        after_discounts = Discount.objects.all().count()

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_discounts, after_discounts)
        self.assertTrue("D013" in str(resp.data["error"]))

    def test_create_discount_past_total_codes_lt_0(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/create")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id': self.establishment1.id }
        request.data = {
            "name": "discount chupiguay",
            "description": "descripción peta",
            "cost": 0.5,
            "totalCodes": -5,
            "initialDate": datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=4)),
            "endDate": 	datetime.datetime.timestamp(datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=10))
        }

        prev_discounts = Discount.objects.all().count()
        resp = Discounts.post(self, request, **url_data)
        after_discounts = Discount.objects.all().count()

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_discounts, after_discounts)
        self.assertTrue("D012" in str(resp.data["error"]))

    def test_create_discount_past_no_payload(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/create")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id': self.establishment1.id }

        prev_discounts = Discount.objects.all().count()
        resp = Discounts.post(self, request, **url_data)
        after_discounts = Discount.objects.all().count()

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_discounts, after_discounts)
        self.assertTrue("Z001" in str(resp.data["error"]))
    
    def test_update_discount_ok(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/<int:discount_id>/update")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id':self.establishment1.id, 'discount_id':self.discount_one.id }
        request.data = {
            "name": self.discount_one.name_text,
            "description": self.discount_one.description_text,
            "cost": self.discount_one.cost_number,
            "totalCodes": 200,
            "initialDate": datetime.datetime.timestamp(self.discount_one.initial_date),
            "scannedCodes": self.discount_one.scannedCodes_number
        }

        resp = Discounts.put(self, request, **url_data)

        discount = Discount.objects.get(id=self.discount_one.id)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(discount.totalCodes_number, 200)
        self.assertEqual(resp.data["msg"], "The discount has been updated")

    def test_update_discount_scanned_codes_below_total(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/<int:discount_id>/update")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id':self.establishment1.id, 'discount_id':self.discount_one.id }
        request.data = {
            "name": self.discount_one.name_text,
            "description": self.discount_one.description_text,
            "cost": self.discount_one.cost_number,
            "totalCodes": self.discount_one.totalCodes_number,
            "initialDate": datetime.datetime.timestamp(self.discount_one.initial_date),
            "scannedCodes": 10
        }

        resp = Discounts.put(self, request, **url_data)

        discount = Discount.objects.get(id=self.discount_one.id)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(discount.scannedCodes_number, 20)
        self.assertTrue("D017" in str(resp.data["error"]))

    def test_delete_discount_ok(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/<int:discount_id>/delete")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id':self.establishment2.id, 'discount_id':self.discount_two.id }

        prev_discounts = Discount.objects.all().count()
        resp = Discounts.delete(self, request, **url_data)
        after_discounts = Discount.objects.all().count()
        

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(prev_discounts-1, after_discounts)
        self.assertEqual(resp.data["msg"], "The discount has been deleted")

    def test_delete_discount_scanned_codes_fail(self):
        token = self.login(self.owner_user.username)
        request = self.factory.post("<int:establishment_id>/discounts/<int:discount_id>/delete")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        url_data = { 'establishment_id':self.establishment1.id, 'discount_id':self.discount_one.id }

        prev_discounts = Discount.objects.all().count()
        resp = Discounts.delete(self, request, **url_data)
        after_discounts = Discount.objects.all().count()
        

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(prev_discounts, after_discounts)
        self.assertTrue("D020" in str(resp.data["error"]))
