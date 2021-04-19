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
    premium = models.BooleanField(default=False)
    premium_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Owner: " + self.user.username


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()

    def __str__(self):
        return "Client: " + self.user.username
