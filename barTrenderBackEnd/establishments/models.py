from django.db import models
from django.core.validators import RegexValidator
from authentication.models import *

class Zone(models.TextChoices):
    AL = "Alameda"
    TR = "Triana"
    MC = "Macarena"
    RM = "Remedios"
    B = "Bermejales"
    C = "Cartuja"
    N = "Nervion"
    SB = "San Bernardo"
    SE = "Sevilla Este"
    BE = "Bellavista"
    EX = "Exterior"


class Establishment(models.Model):
    name_text = models.CharField(max_length=100, blank=False, null=False)
    cif_text = models.CharField(max_length=9, blank=False, null=False, unique=True, validators=[
        RegexValidator(
            regex='^[a-zA-Z]{1}\d{7}[a-zA-Z0-9]{1}$',
            message='It does not match with CIF pattern.'
        )
    ])
    phone_number = models.IntegerField(blank=False, null=False, unique=True, validators=[
        RegexValidator(
            regex="^\d{9}$",
            message='There have to be 9 numbers.'
        )
    ])
    zone_enum = models.CharField(blank=False, null=False, max_length=25, choices=Zone.choices)
    verified_bool = models.BooleanField(default=False)


class Discount(models.Model):
    name_text = models.CharField(max_length=50, blank=False, null=False)
    description_text = models.CharField(max_length=140)
    cost_number = models.FloatField(blank=False, null=False, default=0.0)
    totalCodes_number = models.PositiveIntegerField(blank=True, null=True)
    scannedCodes_number = models.PositiveIntegerField(default=0, blank=False, null=False)
    initial_date = models.DateTimeField(blank=False, null=False)
    end_date = models.DateTimeField(blank=True, null=True)

    # Relations
    clients_id = models.ManyToManyField(Client, blank=True, null=True)
    establishment_id = models.ForeignKey(Establishment, on_delete=models.CASCADE)


# TODO: Intermediate Table that references: Users, Establishments and Discounts (manage num of scanned codes)
