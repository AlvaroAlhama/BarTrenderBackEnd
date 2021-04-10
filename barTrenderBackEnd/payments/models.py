from django.db import models
import datetime
from establishments.models import *


class Payment(models.Model):
    pay_date = models.DateField(blank=True, null=True)
    scanned_number = models.PositiveIntegerField(default=0, blank=False, null=False,  validators=[MinValueValidator(0)])
    discount_id = models.OneToOneField(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return "Payment " + str(self.id) + ": Discount(" + str(self.discount_id.id) + ")"
