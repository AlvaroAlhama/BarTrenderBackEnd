from django.contrib.auth.models import User
from django.test import TransactionTestCase
from stats.models import *
import datetime
from django.core.exceptions import ValidationError


def create_ranking(
        search_date=datetime.datetime.now(),
        filter_enum='Bebida',
        type_text='Cruzcampo',
        value_number=10,
        zone_enum='Triana'
        ):

    return Ranking(
        search_date=search_date,
        filter_enum=filter_enum,
        type_text=type_text,
        value_number=value_number,
        zone_enum=zone_enum
    )


class RankingTestCase(TransactionTestCase):
    def setUp(self):

        # Valid Ranking
        Ranking.objects.create(
            search_date=datetime.datetime.now(),
            filter_enum='Bebida',
            type_text='Cruzcampo',
            value_number=10
        )

    def test_valid_Ranking(self):
        prev_count = Ranking.objects.all().count()
        ranking = create_ranking()
        ranking.save()
        new_count = Ranking.objects.all().count()

        self.assertTrue(new_count - prev_count == 1)

    def test_valid_Ranking_no_zone(self):
        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(type_text='Paulaner', zone_enum=None)
        ranking.save()
        new_count = Ranking.objects.all().count()
        new_ranking = Ranking.objects.filter(search_date=datetime.datetime.now(), filter_enum='Bebida', type_text='Paulaner', value_number=10, zone_enum=None).get()

        self.assertTrue(new_count - prev_count == 1)
        self.assertTrue(new_ranking != None)

    def test_invalid_Ranking_date_null(self):

        prev_count = Ranking.objects.all().count()

        ranking = create_ranking(
            search_date=None
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_filter_enum_name_null(self):

        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            filter_enum=None
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_filter_enum_name_blank(self):

        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            filter_enum=""
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_Ranking_filter_enum_not_exist(self):
        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            filter_enum="B3B1D4S"
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue("Value 'B3B1D4S' is not a valid choice." in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_type_text_name_null(self):

        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            type_text=None
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_type_text_name_blank(self):

        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            type_text=""
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('This field cannot be blank.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_type_text_not_exist(self):
        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            type_text="hsfjdhfkhsfhdkshfkjhfbdnsfbdsmbfdkbfsdbffdsfdsfdsfdsfdsfsfsfdsfshsdhjfbsdfbsjbfjsdbfdhfdjhfkjdshfkdss"
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue("Ensure this value has at most 100 characters (it has 101)." in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_value_number_null(self):

        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            value_number=None
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('This field cannot be null.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_value_number_blank(self):

        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            value_number=""
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('“” value must be an integer.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)

    def test_invalid_value_number_positive(self):

        prev_count = Ranking.objects.all().count()
        ranking = create_ranking(
            value_number=-5
        )

        with self.assertRaises(ValidationError) as context:
            if ranking.full_clean():
                ranking.save()

        new_count = Ranking.objects.all().count()

        self.assertTrue('Ensure this value is greater than or equal to 0.' in str(context.exception))
        self.assertTrue(new_count - prev_count == 0)
