from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Client, Owner
from authentication.views import login, signup, SetPremium, IsPremium, UserInformation
from django.conf import settings
from dateutil.relativedelta import relativedelta
import datetime, pytz
import json

class AuthenticationViewTest(TestCase):

    def login(self, username):
        api_call = "/authentication/login"
        request = self.factory.post(api_call)
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email": str(username), "password":"password"})

        resp = login.post(self, request)

        return resp.data["token"]

    def setUp(self):
        # Users
        self.client_user = User.objects.create_user(username='client@gmail.com', password="password")
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner_user = User.objects.create_user(username='owner@gmail.com', password="password")
        self.owner = Owner.objects.create(phone=954954954,user=self.owner_user)
        self.owner_user_premium = User.objects.create_user(username='owner1@gmail.com', password="password")
        self.owner_premium = Owner.objects.create(phone=954954955,user=self.owner_user_premium, premium=True, premium_end_date=datetime.date.today() + relativedelta(months=+1))
        self.owner_user_premium_past = User.objects.create_user(username='owner2@gmail.com', password="password")
        self.owner_premium_past = Owner.objects.create(phone=954954956,user=self.owner_user_premium_past, premium=True, premium_end_date=datetime.date.today() - relativedelta(months=+1))

        self.factory = RequestFactory()

    def test_login_ok(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"client@gmail.com", "password":"password"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.data["token"])
        self.assertEqual(resp.data['rol'], "client")
        self.assertEqual(resp.data['premium'], False)

    def test_login_premium_ok(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"owner1@gmail.com", "password":"password"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.data["token"])
        self.assertEqual(resp.data['rol'], "owner")
        self.assertEqual(resp.data['premium'], True)

    def test_login_premium_past(self):
        request = self.factory.post("/authentication/login")
        request.headers = {'apiKey': settings.API_KEY, 'Content-Type': 'application/json'}
        request._body = json.dumps({"email":"owner2@gmail.com", "password":"password"})
        resp = login.post(self, request)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.data["token"])
        self.assertEqual(resp.data['rol'], "owner")
        self.assertEqual(resp.data['premium'], False)

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

    def test_get_user_ok(self):
        token = self.login(self.client_user)
        request = self.factory.post("/authentication/user")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        
        resp = UserInformation.get(self, request)
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['name'] == "")
        self.assertTrue(resp.data['surname'] == "")
        self.assertTrue(resp.data['email'] == "client@gmail.com")

    def test_update_info_user_ok(self):
        token = self.login(self.client_user)
        request = self.factory.post("/authentication/user/edit")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"email":"client1@gmail.com", "old_password":"password", "name":"Nombre", "surname":"Apellido", "password":"Vekto1234$", "birthday":946681200}
        
        resp1 = UserInformation.put(self, request)

        token = resp1.data['token']
        request = self.factory.post("/authentication/user")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        
        resp = UserInformation.get(self, request)
        
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['name'] == "Nombre")
        self.assertTrue(resp.data['surname'] == "Apellido")
        self.assertTrue(resp.data['email'] == "client1@gmail.com")

    def test_update_info_user_bad_birthday(self):
        token = self.login(self.client_user)
        request = self.factory.post("/authentication/user/edit")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"email":"client1@gmail.com", "old_password":"password", "name":"Nombre", "surname":"Apellido", "password":"Vekto1234$"}
        
        resp = UserInformation.put(self, request)
        
        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Z001" in str(resp.data["error"]))

    def test_update_info_user_bad_phone(self):
        token = self.login(self.client_user)
        request = self.factory.post("/authentication/user/edit")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        request.data = {"email":"owner@gmail.com", "old_password":"password", "name":"Nombre", "surname":"Apellido", "password":"Vekto1234$"}
        
        resp = UserInformation.put(self, request)
        
        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Z001" in str(resp.data["error"]))

    def test_isPremium_true(self):
        token = self.login(self.owner_user_premium)
        request = self.factory.post("/authentication/user/ispremium")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        
        resp = IsPremium.get(self, request)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["isPremium"], True)

    def test_isPremium_false(self):
        token = self.login(self.owner_user)
        request = self.factory.post("/authentication/user/ispremium")
        request.headers = {'token': token, 'Content-Type': 'application/json'}
        
        resp = IsPremium.get(self, request)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["isPremium"], False)