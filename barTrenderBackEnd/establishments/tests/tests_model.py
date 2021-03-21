from django.contrib.auth.models import User
from django.test import TransactionTestCase
from ..models import *
from authentication.models import *
import datetime


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


def create_discount(
        name="Test Descuento Ejemplo 1",
        description="Test Ejemplo Descripcion",
        costs=1.0,
        total_codes=None,
        scanned_codes=0,
        initial_date=timezone.now(),
        end_date=None):

    establishment = Establishment.objects.get(name_text="Bar Ejemplo Dos")

    return Discount(
        name_text=name,
        description_text=description,
        cost_number=costs,
        totalCodes_number=total_codes,
        scannedCodes_number=scanned_codes,
        initial_date=initial_date+datetime.timedelta(days=20),
        end_date=end_date,
        establishment_id=establishment
    )


class EstablishmentsTestCase(TransactionTestCase):
    def setUp(self):

        # User
        user_owner = User.objects.create_user('owner@gmail.com')
        user_client = User.objects.create_user('client@gmail.com')

        # Owner
        owner = Owner.objects.create(phone="123456789", user=user_owner)
        client = Client.objects.create(birthday=datetime.datetime.now(),user=user_client)

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


class DiscountsTestCases(TransactionTestCase):
    def setUp(self):
        # User
        user_owner = User.objects.create_user('owner@gmail.com')
        user_client = User.objects.create_user('client@gmail.com')

        # Owner
        owner = Owner.objects.create(phone="123456789", user=user_owner)
        client = Client.objects.create(birthday=datetime.datetime.now(), user=user_client)

        # Valid Establishments
        establishment = Establishment.objects.create(
            name_text="Bar Ejemplo Dos",
            cif_text="B56316524",
            phone_number="123456789",
            zone_enum="Alameda",
            verified_bool=True,
            owner=owner
        )

        # Valid Discount
        discount = Discount.objects.create(
            name_text="Descuento Ejemplo Uno",
            description_text="Ejemplo Descripcion",
            cost_number=1.0,
            totalCodes_number=None,
            scannedCodes_number=0,
            initial_date=timezone.now()+datetime.timedelta(days=40),
            end_date=None,
            establishment_id=establishment
        )

        discount.clients_id.add(client)

    def test_valid_discount(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now()+ datetime.timedelta(days=40))
        discount.save()
        discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue(new_count - prev_count == 1)

    def test_invalid_discount_name_blank(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), name="")

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_discount_name_null(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), name=None)

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_discount_name_length(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(
            initial_date=timezone.now() + datetime.timedelta(days=40),
            name="fshjkfhskjhfkdhfkdhskfhdksjhfkjshfkjhskjfhskhfskhfdshjkfhjskh"
        )

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('Ensure this value has at most 50 characters (it has 61).' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_discount_description_length(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(
            initial_date=timezone.now() + datetime.timedelta(days=40),
            description="""fshjkfhskjhfkdhfkdhskfhdksjhfkjshfkjhskjfhskhfskhfdshjkfhjskh
                            fskflskfñldklñfksñlfkñlskfñlskfñlskfñlskñfldksñlfkñlskfñdlskf
                        """
        )

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('Ensure this value has at most 140 characters (it has 176).' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    # Cannot be tested
    """def test_invalid_discount_cost_blank(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), costs="")

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)"""

    def test_invalid_discount_cost_null(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), costs=None)

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_discount_cost_negative(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), costs=-5.0)

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('Ensure this value is greater than or equal to 0.0.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_discount_total_codes_negative(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), total_codes=-5)

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('Ensure this value is greater than or equal to 0.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    # Cannot be tested
    """def test_invalid_discount_total_scanned_codes_blank(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), scanned_codes="")

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)"""

    def test_invalid_discount_total_scanned_codes_null(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), scanned_codes=None)

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_discount_total_scanned_codes_negative(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() + datetime.timedelta(days=40), scanned_codes=-5)

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('Ensure this value is greater than or equal to 0.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    # Cannot be tested
    """def test_invalid_discount_initial_date_blank(self):
        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date="")

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('Ensure this value is greater than or equal to 0.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)"""

    # Cannot be tested
    """def test_invalid_discount_initial_date_null(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=None)

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)"""

    def test_invalid_discount_initial_date_past(self):

        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(initial_date=timezone.now() - datetime.timedelta(days=40))

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('Initial Date cannot be in the past. Check date and Time' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_discount_end_date_before_initial(self):
        client = Client.objects.get(user=User.objects.get(username='client@gmail.com'))
        prev_count = Discount.objects.all().count()

        discount = create_discount(end_date=timezone.now() - datetime.timedelta(days=40), )

        with self.assertRaises(ValidationError) as context:
            if discount.full_clean():
                discount.save()
                discount.clients_id.add(client)

        new_count = Discount.objects.all().count()

        self.assertTrue('End datetime must be greater than start datetime' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)
