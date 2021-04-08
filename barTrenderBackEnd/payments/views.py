from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from establishments.models import *
from establishments.utils import *
from .models import *
from authentication.decorators import token_required, apikey_required
import json
import math
from .utils import *


class CalculatePayment(APIView):
    @token_required("owner")
    def get(self, request, establishment_id):

        owner = get_owner(request)

        validations = validate_establishment(establishment_id)
        if validations is not None:
            return validations

        validations = validate_establishment_owner(establishment_id, owner)
        if validations is not None:
            return validations

        discounts = Discount.objects.filter(establishment_id=establishment_id)
        payments = Payment.objects.all()

        cost = {"payments": [], "total": 0}
        for payment in payments:
            if payment.discount_id in discounts and (payment.pay_date is not None or payment.pay_date is not ""):

                to_pay = get_commission(payment.discount_id.cost_number, payment.scanned_number)

                cost["payments"].append(
                    {
                        "discount": payment.discount_id.id,
                        "value": to_pay
                    }
                )
                cost["total"] += to_pay

        return HttpResponse(json.dumps(cost), 200)
