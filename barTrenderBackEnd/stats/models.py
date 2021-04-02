from django.db import models
from establishments.models import Type
from django.core.validators import MinValueValidator


class Counter(models.Model):
    search_date = models.DateField(blank=False, null=False)
    filter_enum = models.CharField(blank=False, null=False, max_length=25, choices=Type.choices)
    type_text = models.CharField(max_length=100, blank=False, null=False)
    value_number = models.PositiveIntegerField(default=0, blank=False, null=False, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.type_text + " (" + str(self.search_date) + ")"

    class Meta:
        app_label = 'stats'
