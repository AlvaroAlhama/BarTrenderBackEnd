from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNumber = models.IntegerField()

    def __str__(self):
        return "Owner: " + self.user.username

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()

    def __str__(self):
        return "Client: " + self.user.username

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
    owner = models.OneToOneField(Owner, on_delete=models.CASCADE)

    def __str__(self):
        return "Establisment: " + self.name_text