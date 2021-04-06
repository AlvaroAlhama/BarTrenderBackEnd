from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Client, Owner
from authentication.views import login, signup
from django.conf import settings
import datetime
import json

class AuthenticationViewTest(TestCase):

    def setUp(self):
        # Users
        self.client_user = User.objects.create_user(username='client@gmail.com', password="password")
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner_user = User.objects.create_user(username='owner@gmail.com', password="password")
        self.owner = Owner.objects.create(phone=954954954,user=self.owner_user)

        self.factory = RequestFactory()

    def test_login_ok(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client@gmail.com", "password":"password"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.data["token"])
        self.assertEqual(resp.data['rol'], "client")

    def test_login_bad_password(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client@gmail.com", "password":"bad"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 401)
        self.assertTrue('A009' in str(resp.data["error"]))

    def test_login_bad_user(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"fake@gmail.com", "password":"password"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 401)
        self.assertTrue('A009' in str(resp.data["error"]))

    def test_login_bad_request_data(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client@gmail.com"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 401)
        self.assertTrue('Z001' in str(resp.data["error"]))
    
    def test_bad_apiKey(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': "badApiKey", 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client@gmail.com", "password":"password"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 401)
        self.assertTrue('A004' in str(resp.data["error"]))

    def test_no_apiKey(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client@gmail.com", "password":"password"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 401)
        self.assertTrue('A003' in str(resp.data["error"]))

    def test_signup_client_ok(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client11@gmail.com", "password":"C0mplexpa$$","rol":"client", "birthday":946681200})
        
        prev_count = Client.objects.all().count()
        resp = signup.post(self, request)
        new_count = Client.objects.all().count()

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(new_count - prev_count == 1)
        self.assertIsNotNone(resp.data["token"])
        self.assertEqual(resp.data['rol'], "client")
        self.assertEqual(resp.data["msg"], "Usuario creado correctamente")

    def test_signup_owner_ok(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"user11@gmail.com", "password":"C0mplexpa$$","rol":"owner", "phone":123456789})
        
        prev_count = Owner.objects.all().count()
        resp = signup.post(self, request)
        new_count = Owner.objects.all().count()
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(new_count - prev_count == 1)
        self.assertIsNotNone(resp.data["token"])
        self.assertEqual(resp.data['rol'], "owner")
        self.assertEqual(resp.data["msg"], "Usuario creado correctamente")

    def test_signup_client_no_birthday(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client11@gmail.com", "password":"C0mplexpa$$","rol":"client"})
        
        prev_count = Client.objects.all().count()
        resp = signup.post(self, request)
        new_count = Client.objects.all().count()
        
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(new_count - prev_count == 0)
        self.assertTrue("Z001" in str(resp.data["error"]))

    def test_signup_client_bad_birthday(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client11@gmail.com", "password":"C0mplexpa$$","rol":"client", "birthday":"946681200"})
        
        prev_count = Client.objects.all().count()
        resp = signup.post(self, request)
        new_count = Client.objects.all().count()
        
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(new_count - prev_count == 0)
        self.assertTrue("Z002" in str(resp.data["error"]))

    def test_signup_owner_no_phone(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"owner12@gmail.com", "password":"C0mplexpa$$","rol":"owner"})
        
        prev_count = Owner.objects.all().count()
        resp = signup.post(self, request)
        new_count = Owner.objects.all().count()
        
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(new_count - prev_count == 0)
        self.assertTrue("Z001" in str(resp.data["error"]))

    def test_signup_owner_bad_phone(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"owner12@gmail.com", "password":"C0mplexpa$$","rol":"owner", "phone":12345678})
        
        prev_count = Owner.objects.all().count()
        resp = signup.post(self, request)
        new_count = Owner.objects.all().count()
        
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(new_count - prev_count == 0)
        self.assertTrue("Z003" in str(resp.data["error"]))

    def test_signup_bad_body(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"password":"C0mplexpa$$","rol":"client", "birthday":946681200})
        
        prev_count = Client.objects.all().count()
        resp = signup.post(self, request)
        new_count = Client.objects.all().count()
        
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(new_count - prev_count == 0)
        self.assertTrue("Z001" in str(resp.data["error"]))

    def test_signup_already_exists(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client@gmail.com", "password":"C0mplexpa$$","rol":"client", "birthday":946681200})
        
        resp = signup.post(self, request)
        
        self.assertEqual(resp.status_code, 400)
        self.assertTrue("A013" in str(resp.data["error"]))

    def test_signup_bad_password(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client11@gmail.com", "password":"password12","rol":"client", "birthday":946681200})
        
        prev_count = Client.objects.all().count()
        resp = signup.post(self, request)
        new_count = Client.objects.all().count()
        
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(new_count - prev_count == 0)
        self.assertTrue("A016" in str(resp.data["error"]))
    
    def test_signup_bad_rol(self):
        request = self.factory.post("/authentication/signup")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client11@gmail.com", "password":"C0mplexpa$$","rol":"noexists", "birthday":946681200})
        
        prev_count = Client.objects.all().count()
        resp = signup.post(self, request)
        new_count = Client.objects.all().count()
        
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(new_count - prev_count == 0)
        self.assertTrue("A011" in str(resp.data["error"]))