from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from establishments.models import *
from establishments.utils import *
from .models import *
from authentication.decorators import token_required, apikey_required
import json
import math
from .utils import *
import barTrenderBackEnd.errors
import datetime


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
            if payment.discount_id in discounts and (payment.pay_date is not None or payment.pay_date != ""):

                to_pay = get_commission(payment.discount_id.cost_number, payment.scanned_number)

                cost["payments"].append(
                    {
                        "discount": payment.discount_id.id,
                        "payment_date": str(payment.pay_date),
                        "value": to_pay
                    }
                )
                cost["total"] += to_pay

        return Response(cost, "200")


class MakePayment(APIView):
    @token_required("owner")
    def post(self, request, establishment_id):

        owner = get_owner(request)

        validations = validate_establishment(establishment_id)
        if validations is not None:
            return validations

        validations = validate_establishment_owner(establishment_id, owner)
        if validations is not None:
            return validations

        try:
            # Get discounts from establishment_id
            discounts = Discount.objects.filter(establishment_id=establishment_id)

            # Get all payments
            payments = Payment.objects.all()

            for payment in payments:
                if payment.discount_id in discounts \
                        and (payment.pay_date is not None or payment.pay_date != "")\
                        and payment.scanned_number != 0:

                    discount = payment.discount_id

                    if discount.end_date is not None and discount.end_date <= timezone.now():
                        payment.pay_date = None
                    else:
                        payment.pay_date = timezone.now() + datetime.timedelta(days=30)

                    payment.scanned_number = 0
                    payment.save()
        except Exception as e:
            return generate_response("E00X", 400)

        return generate_response({"msg": "Los pagos se han actualizado correctamente"}, "200")
