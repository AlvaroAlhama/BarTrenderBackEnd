import os, base64, math, requests, json, datetime
from django.http import HttpResponse
from rest_framework.views import Response

def truncate(number, decimals=0):

    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


def get_commission(cost, scanned_num):

    percentage = 0.0
    if 0.5 <= cost < 2.0:
        percentage = 0.025
    elif 2 <= cost < 7.0:
        percentage = 0.03
    elif cost >= 7.0:
        percentage = 0.05

    return truncate(cost * scanned_num * percentage, 2)

def validate_paypal_payment(order_id, create_time):
    
    token = get_paypal_token(os.environ.get('PAYPAL_CLIENT_ID'), os.environ.get('PAYPAL_CLIENT_SECRET'))
    if token["statusCode"] != 200: return token
    else: token = token['token']

    order = paypal_api_call_order(order_id, token)
    if order.status_code != 200: return order.data["error"]

    if order.data['status'] != "COMPLETED": return "P001"

    formatted_date = datetime.datetime.strptime(create_time.replace("Z", "").replace("T", " "), '%Y-%m-%d %H:%M:%S')
    if order.data['create_time'] != create_time or formatted_date > datetime.datetime.now() or formatted_date < datetime.datetime.now() - datetime.timedelta(days=1): 
        return "P002"


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
        return "API001"
    else:
        return {"token": json.loads(token.content)['access_token'], "statusCode": 200}


def paypal_api_call_order(order_id, token):

    host = "https://api.sandbox.paypal.com/"
    url = host + "v2/checkout/orders/" + str(order_id)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    }

    orders = requests.get(url, headers=headers)
    
    if orders.status_code != 200:
        return Response({"error": "API002"}, 400)
    else:
        data = json.loads(orders.content)

        return Response(
            {
                "status": data['status'],
                "create_time": data["create_time"]
            }, 200)