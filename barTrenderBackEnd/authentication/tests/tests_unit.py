from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from authentication.models import Client, Owner
from authentication.decorators import token_required, apikey_required
from rest_framework.response import Response
from django.conf import settings
import authentication.utils as utils
import datetime


class AuthenticationUnitTest(TestCase):
    
    def setUp(self):
        # Users
        self.client_user = User.objects.create_user('client@gmail.com')
        self.owner_user = User.objects.create_user('owner@gmail.com')
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner = Owner.objects.create(phone="123456789", user=self.owner_user)
        self.client_token = utils.getToken(self.client_user, 'client')[0]

        self.factory = RequestFactory()
    
    def test_get_rol(self):
        rol = utils.getRol(self.owner_user)
        self.assertEqual(rol,"owner")
    
    def test_get_token(self):
        token = utils.getToken(self.client_user, 'client')
        self.assertEqual(len(token),2)

    def test_validate_token_OK(self):
        error = utils.validateToken(self.client_token, "client")
        self.assertEqual(error, None)

    def test_validate_token_Error(self):
        error = utils.validateToken(self.client_token, "owner")
        self.assertEqual(error, "A008")

    def test_get_user_from_token(self):
        user = utils.getUserFromToken(self.client_token)
        self.assertEqual(user, self.client_user)

    def test_apiKey_decorator_OK(self):
        @apikey_required
        def view(self,request):
            return Response("OK", 200)

        request = self.factory.get("/path")
        request.headers = {'apiKey': settings.API_KEY}
        resp = view(self,request)
        self.assertEqual(resp.status_code, 200)

    def test_apiKey_decorator_FAIL(self):
        @apikey_required
        def view(self,request):
            return Response("OK", 200)

        request = self.factory.get("/path")
        request.headers = {'apiKey': "InvalidApiKey"}
        resp = view(self,request)
        self.assertEqual(resp.status_code, 401)

    def test_token_decorator_OK(self):
        @token_required('all')
        def view(self,request):
            return Response("OK", 200)

        request = self.factory.get("/path")
        request.headers = {'token': self.client_token}
        resp = view(self,request)
        self.assertEqual(resp.status_code, 200)

    def test_token_decorator_InvalidToken(self):
        @token_required('owner')
        def view(self,request):
            return Response("OK", 200)

        request = self.factory.get("/path")
        request.headers = {'token': "Invalid Token"}
        resp = view(self,request)
        self.assertEqual(resp.status_code, 401)
    
    def test_token_decorator_InvalidRol(self):
        @token_required('owner')
        def view(self,request):
            return Response("OK", 200)

        request = self.factory.get("/path")
        request.headers = {'token': self.client_token}
        resp = view(self,request)
        self.assertEqual(resp.status_code, 401)

    def test_token_decorator_NoToken(self):
        @token_required('all')
        def view(self,request):
            return Response("OK", 200)

        request = self.factory.get("/path")
        request.headers = {'token': None}
        resp = view(self,request)
        self.assertEqual(resp.status_code, 401)