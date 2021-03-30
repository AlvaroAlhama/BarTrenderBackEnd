from django.test import TestCase
from django.contrib.auth.models import User
from authentication.models import Client, Owner
import authentication.utils as utils
import datetime


# Unit
class AuthenticationUnitTest(TestCase):
    
    def setUp(self):
        # Users
        self.client_user = User.objects.create_user('client@gmail.com')
        self.owner_user = User.objects.create_user('owner@gmail.com')
        self.client = Client.objects.create(birthday=datetime.datetime.now(),user=self.client_user)
        self.owner = Owner.objects.create(phone="123456789", user=self.owner_user)
    
    def test_get_token(self):
        token = utils.getToken(self.client_user, 'client')
        self.assertEqual(len(token),2)


# Model
