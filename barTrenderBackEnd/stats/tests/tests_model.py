from django.contrib.auth.models import User
from django.test import TransactionTestCase
from stats.models import *
from authentication.models import *
import datetime
from django.core.exceptions import ValidationError


def create_counter(
        search_date=datetime.datetime.now(),
        filter_enum='Bebida',
        type_text='Cruzcampo',
        value_number=10
        ):

    return Counter(
        search_date=search_date,
        filter_enum=filter_enum,
        type_text=type_text,
        value_number=value_number
    )


class CounterTestCase(TransactionTestCase):
    def setUp(self):

        # Valid Counter
        Counter.objects.create(
            search_date=datetime.datetime.now(),
            filter_enum='Bebida',
            type_text='Cruzcampo',
            value_number=10
        )

    def test_valid_counter(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter()
        counter.save()
        new_count = Counter.objects.all().count()

        self.assertTrue(new_count - prev_count == 1)

    def test_invalid_counter_date_null(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            search_date=None
        )

        with self.assertRaises(Exception) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_filter_enum_name_null(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            filter_enum=None
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_filter_enum_name_blank(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            filter_enum=""
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_counter_filter_enum_not_exist(self):
        prev_count = Counter.objects.all().count()
        counter = create_counter(
            filter_enum="B3B1D4S"
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue("Value 'B3B1D4S' is not a valid choice." in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_type_text_name_null(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            type_text=None
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_type_text_name_blank(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            type_text=""
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_type_text_not_exist(self):
        prev_count = Counter.objects.all().count()
        counter = create_counter(
            type_text="hsfjdhfkhsfhdkshfkjhfbdnsfbdsmbfdkbfsdbffdsfdsfdsfdsfdsfsfsfdsfshsdhjfbsdfbsjbfjsdbfdhfdjhfkjdshfkdss"
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue("Ensure this value has at most 100 characters (it has 101)." in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_value_number_null(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            value_number=None
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_value_number_blank(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            value_number=""
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('“” value must be an integer.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_value_number_positive(self):

        prev_count = Counter.objects.all().count()
        counter = create_counter(
            value_number=-5
        )

        with self.assertRaises(ValidationError) as context:
            if counter.full_clean():
                counter.save()

        new_count = Counter.objects.all().count()

        self.assertTrue('Ensure this value is greater than or equal to 0.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)
