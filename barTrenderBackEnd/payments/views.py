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
import base64
import requests
import os
import ast


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

        token = get_paypal_token(os.environ.get('PAYPAL_CLIENT_ID'), os.environ.get('PAYPAL_CLIENT_SECRET'))
        if token.status_code != 200:
            return token
        else:
            token = token.data['token']

        order = paypal_api_call_order(request.data['order_id'], token)
        if order.status_code != 200:
            return order

        if order.data['status'] != "COMPLETED":
            return generate_response("P001", 400)

        if order.data['create_time'] != request.data['create_time']:
            return generate_response("P002", 400)

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

        return Response({"msg": "Los pagos se han actualizado correctamente"}, "200")


def get_paypal_token(client_id, client_secret):
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {0}".format(base64.b64encode((client_id + ":" + client_secret).encode()).decode())
    }

    token = requests.post(url, data, headers=headers)

    if token.status_code != 200:
        return generate_response("API001", 400)
    else:
        return Response({"token": json.loads(token.content)['access_token']}, 200)


def paypal_api_call_order(order_id, token):
    host = "https://api.sandbox.paypal.com/"
    url = host + "v2/checkout/orders/" + str(order_id)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }

    orders = requests.get(url, headers=headers)

    if orders.status_code != 200:
        return generate_response("API002", 400)
    else:
        data = json.loads(orders.content)

        return Response(
            {
                "status": data['status'],
                "create_time": data["create_time"]
            }, 200)
