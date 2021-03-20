from django.core.exceptions import ValidationError
from django.forms import forms
from django.utils import timezone


def date_is_before_now(value):

    if value < timezone.now():
        raise ValidationError("Initial Date cannot be in the past. Check date and Time")


def validate_date(self):

    if self.end_date is not None:
        initial_date = self.initial_date
        end_date = self.end_date

        if end_date <= initial_date:
            raise forms.ValidationError({'end_date': ["End datetime must be greater than start datetime"]})

        return end_date


def validate_cif(value):

    letters = 'ABCDEFGHPQSKLMX'

    first_letter = str(value)[0]
    last_letter = str(value)[-1]

    if first_letter not in letters:
        raise ValidationError("No valid CIF. Please try again.")

    strip_value = str(value)[1:len(value)-1]

    sum_digits = 0
    for i, values in enumerate(strip_value):
        num = int(values)

        if i % 2 != 0:
            sum_digits += num
        else:
            num = num * 2
            for digit in str(num):
                sum_digits += int(digit)

    unit = sum_digits % 10
    control_code = 10 - unit

    if first_letter == 'X' or first_letter == 'P':
        control_code += 64

    if str(control_code) != last_letter:
        raise ValidationError("No valid CIF. Please try again.")
