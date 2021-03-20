from django.contrib.auth.models import User
from django.test import TransactionTestCase
from ..models import *
from authentication.models import *


def create_establishment(
        name="Test Bar Ejemplo 1",
        cif="H72631351",
        phone=111111111,
        zone="Alameda",
        verified=True):

    user = User.objects.get(username='owner@gmail.com')
    owner = Owner.objects.get(user=user)

    return Establishment(
        name_text=name,
        cif_text=cif,
        phone_number=phone,
        zone_enum=zone,
        verified_bool=verified,
        owner=owner
    )


class EstablishmentsTestCase(TransactionTestCase):
    def setUp(self):

        # User
        user = User.objects.create_user('owner@gmail.com')

        # Owner
        owner = Owner.objects.create(phone="123456789", user=user)

        # Valid Establishments
        Establishment.objects.create(
            name_text="Bar Ejemplo Uno",
            cif_text="B56316524",
            phone_number="123456789",
            zone_enum="Alameda",
            verified_bool=True,
            owner=owner
        )

    def test_valid_establishment(self):

        prev_count = Establishment.objects.all().count()
        establishment = create_establishment()
        establishment.save()
        new_count = Establishment.objects.all().count()

        self.assertTrue(new_count - prev_count == 1)

    def test_invalid_establishment_owner_null(self):

        prev_count = Establishment.objects.all().count()
        establishment = create_establishment()
        establishment.owner = None

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_name_blank(self):

        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(name="")

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_name_null(self):

        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(name=None)

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_name_length(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(
            name='kjfklsjhfkjeshfjksdhfjkdshfkjsdhfkjdshjkfhdskdfhsdkhfhsjkhfddahdsajdjksahdkjhsakjdhkjashdkjashdkjasja'
        )

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('Ensure this value has at most 100 characters (it has 101).' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_cif(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(cif="Q000000J")

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('It does not match with CIF pattern.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_cif_blank(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(cif="")

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_cif_null(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(cif=None)

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_cif_unique(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(cif='B56316524')

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('Establishment with this Cif text already exists.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_phone(self):

        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(phone=1234567890)

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('“%(value)s” value must be an integer.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_phone_blank(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(phone="")

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('“” value must be an integer.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_phone_null(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(phone=None)

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_phone_unique(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(phone=123456789)

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('Establishment with this Phone number already exists.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_zone_value(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(zone="Test")

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()
        self.assertTrue("Value 'Test' is not a valid choice." in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_zone_blank(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(zone="")

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_establishment_zone_null(self):
        prev_count = Establishment.objects.all().count()
        establishment = create_establishment(zone=None)

        with self.assertRaises(ValidationError) as context:
            if establishment.full_clean():
                establishment.save()

        new_count = Establishment.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)
