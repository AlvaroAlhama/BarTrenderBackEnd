from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.IntegerField(blank=False, null=False, unique=True, validators=[
        RegexValidator(
            regex=r"^\d{9}$",
            message='There have to be 9 numbers.'
        )
    ])

    def __str__(self):
        return "Owner: " + self.user.username

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()

    def __str__(self):
        return "Client: " + self.user.username

class Type(models.TextChoices):
    B = "Bebida"
    E = "Estilo"
    I = "Instalación"
    O = "Ocio"
    T = "Tapa"

class Tag(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    type = models.CharField(blank=False, null=False, max_length=25, choices=Type.choices)

    def __str__(self):
        return "Tag: " + self.name + " Type: " + self.type

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
    name = models.CharField(max_length=100, blank=False, null=False)
    cif = models.CharField(max_length=9, blank=False, null=False, unique=True, validators=[
        RegexValidator(
            regex=r'^[a-zA-Z]{1}\d{7}[a-zA-Z0-9]{1}$',
            message='It is not a valid CIF'
        )
    ])
    phone = models.IntegerField(blank=False, null=False, unique=True, validators=[
        RegexValidator(
            regex=r"^\d{9}$",
            message='There have to be 9 numbers.'
        )
    ])
    zone = models.CharField(blank=False, null=False, max_length=25, choices=Zone.choices)
    verified = models.BooleanField(default=False)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return "Establisment: " + self.name