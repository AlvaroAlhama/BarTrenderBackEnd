from django.test import TransactionTestCase
from authentication.models import Owner, Client
from django.contrib.auth.models import User

class AuthenticationModelTest(TransactionTestCase):

    def setUp(self):
        self.client_user = User.objects.create_user('client@gmail.com')
        self.owner_user = User.objects.create_user('owner@gmail.com')

    def test_create_owner_ok(self):
        prev_count = Owner.objects.all().count()
        owner = Owner(user=self.owner_user, phone=955123456)
        owner.save()
        new_count = Owner.objects.all().count()

        self.assertTrue(new_count - prev_count == 1)

    def test_create_owner_no_user(self):
        prev_count = Owner.objects.all().count()
        owner = Owner(user=None, phone=955123456)

        with self.assertRaises(Exception) as context:
            if owner.full_clean():
                owner.save()

        new_count = Owner.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_create_owner_no_phone(self):
        prev_count = Owner.objects.all().count()
        owner = Owner(user=self.owner_user, phone=None)

        with self.assertRaises(Exception) as context:
            if owner.full_clean():
                owner.save()

        new_count = Owner.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_create_owner_incorrect_phone(self):
        prev_count = Owner.objects.all().count()
        owner = Owner(user=self.owner_user, phone=955)

        with self.assertRaises(Exception) as context:
            if owner.full_clean():
                owner.save()

        new_count = Owner.objects.all().count()

        self.assertTrue("value must be an integer.",str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_create_owner_unique_phone(self):
        owner = Owner(user=User.objects.create_user('owner2@gmail.com'), phone=123456789)
        owner.save()

        prev_count = Owner.objects.all().count()
        owner = Owner(user=User.objects.create_user('owner3@gmail.com'), phone=123456789)

        with self.assertRaises(Exception) as context:
            if owner.full_clean():
                owner.save()

        new_count = Owner.objects.all().count()

        self.assertTrue("Owner with this Phone already exists." in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_create_client_ok(self):
        prev_count = Client.objects.all().count()
        client = Client(user=self.client_user, birthday="2000-01-01")
        client.save()
        new_count = Client.objects.all().count()

        self.assertTrue(new_count - prev_count == 1)

    def test_create_client_no_user(self):
        prev_count = Client.objects.all().count()
        client = Client(user=None, birthday="2000-01-01")

        with self.assertRaises(Exception) as context:
            if client.full_clean():
                client.save()

        new_count = Client.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_create_client_invalid_birthday(self):
        prev_count = Client.objects.all().count()
        client = Client(user=None, birthday="2000-14-01")

        with self.assertRaises(Exception) as context:
            if client.full_clean():
                client.save()

        new_count = Client.objects.all().count()

        self.assertTrue('“2000-14-01” value has the correct format (YYYY-MM-DD) but it is an invalid date' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

