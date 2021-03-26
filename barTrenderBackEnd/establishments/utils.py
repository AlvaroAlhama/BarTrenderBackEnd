from rest_framework.response import Response
import qrcode
import hashlib
import datetime
import time
import io
from authentication.utils import *
from .models import *
from django.utils import timezone
from django.db.models import Q, F
from datetime import datetime

# ERROR MSG

errors = {
    'A001': 'Client no existe',
    'A002': 'Client no existe',
    'E001': 'Establecimiento no existe',
    'E002': 'El establecimiento no pertenece al dueño',
    'D001': 'Descuento no existe',
    'D002': 'Descuento no pertenece al establecimiento',
    'D003': 'El descuento ha expirado',
    'D004': 'No quedan descuentos disponibles',
    'D005': 'Descuento ya escaneado por usuario',
    'D010': 'Campos obligatorios no proporcionados',
    'D011': 'El coste no puede ser menor que 0',
    'D012': 'El total de códigos no puede ser menor que 0',
    'D013': 'La fecha inicial no puede estar en el pasado',
    'D014': 'La fecha de finalización debe ser posterior a la inicial',
    'D015': 'El total de códigos no puede ser menor que 0 ni que el número de códigos escaneados',
    'D016': 'La fecha de finalización debe ser posterior a la inicial y posterior a la actual',
    'D017': 'Los parámetros nombre, descripción, coste, fecha de inicio y códigos escaneados no pueden ser modificados una vez empezado el descuento',
    'D018': 'El número de códigos escaneados no puede ser diferente de 0',
    'D019': 'No se puede modificar un descuento que haya caducado',
}


def generate_response(code, status):
    body = {
        'error': str(code) + ": " + errors[code]
    }

    return Response(body, status)


def validate_discount(establishment_id, discount_id):
    # Validate Discount
    try:
        discount = Discount.objects.get(id=discount_id)

        if discount.establishment_id.id != establishment_id:
            # Return error 400: Bad Request
            return generate_response("D002", '400')
    except Discount.DoesNotExist:
        # Error: object does not exist, return 404
        return generate_response("D001", '404')

def validate_discount_request(discount):
    if "name" not in discount or "description" not in discount or "cost" not in discount or "initialDate" not in discount:
        return generate_response("D010", "400")

    if discount["name"]=="" or discount["description"]=="" or discount["cost"]=="" or discount["initialDate"]=="" or discount["name"]==None or discount["description"]==None or discount["cost"]==None or discount["initialDate"]==None:
        return generate_response("D010", "400")

    if discount["cost"] < 0: return generate_response("D011", "400")

    if "totalCodes" in discount:
        if discount["totalCodes"] <= 0 : return generate_response("D012", "400")
    
    if discount["initialDate"] < time.time() - 10: return generate_response("D013", "400")

    if "endDate" in discount:
        if discount["endDate"] < discount["initialDate"]: return generate_response("D014", "400")

def validate_discount_update(discount, discount_id):
    if "name" not in discount or "description" not in discount or "cost" not in discount or "initialDate" not in discount:
        return generate_response("D010", "400"), None

    if (discount["name"]=="" or discount["description"]=="" or discount["cost"]=="" or discount["initialDate"]=="" 
    or discount["name"]==None or discount["description"]==None or discount["cost"]==None or discount["initialDate"]==None):
        return generate_response("D010", "400"), None
    
    discount_stored = Discount.objects.get(id=discount_id)

    if datetime.timestamp(discount_stored.initial_date) > time.time():

        if discount["cost"] < 0: return generate_response("D011", "400"), None

        if "totalCodes" in discount:
            if discount["totalCodes"] <= 0 : return generate_response("D012", "400"), None
        
        if discount["initialDate"] < time.time() - 10: return generate_response("D013", "400"), None

        if "endDate" in discount:
            if discount["endDate"] < discount["initialDate"]: return generate_response("D014", "400"), None

        if "scannedCodes" in discount:
            if discount["scannedCodes"] == 0: return generate_response("D018", "400"), None
    
    elif ((datetime.timestamp(discount_stored.initial_date) < time.time() and discount_stored.scannedCodes_number < discount_stored.totalCodes_number) 
    or (datetime.timestamp(discount_stored.initial_date) < time.time() and discount_stored.end_date != None and datetime.timestamp(discount_stored.initial_date) < time.time())
    or (datetime.timestamp(discount_stored.initial_date) < time.time() and discount_stored.scannedCodes_number < discount_stored.totalCodes_number 
    and discount_stored.end_date != None and datetime.timestamp(discount_stored.initial_date) < time.time())):

        if "totalCodes" in discount:
            if discount["totalCodes"] <= 0 or discount['totalCodes'] < discount_stored.scannedCodes_number : return generate_response("D015", "400"), None

        if "endDate" in discount:
            if discount["endDate"] < discount["initialDate"] or discount['endDate'] < time.time(): return generate_response("D016", "400"), None

        if (discount_stored.name_text != discount['name'] or discount_stored.description_text != discount['description']
        or discount_stored.cost_number != discount['cost'] or datetime.timestamp(discount_stored.initial_date) != discount["initialDate"]
        or discount_stored.scannedCodes_number != discount['scannedCodes']):
            return generate_response("D017", "400"), None

    else:
        return generate_response("D019", "400"), None

    return None, discount_stored


def validate_establishment(establishment_id):
    # Validate Establishment
    try:
        Establishment.objects.get(id=establishment_id)
    except Establishment.DoesNotExist:
        # Error: object does not exist, return 404
        return generate_response("E002", '404')


def validate_conditions(client, discount_id):
    # User
    discount = Discount.objects.get(id=discount_id)

    # Check if the code is going to be scanned in time
    if discount.end_date is not None:
        if timezone.now() > discount.end_date:
            return generate_response("D003", '400')

    # Check there are available QR Codes when they are limited
    if discount.totalCodes_number is not None:
        if discount.totalCodes_number - discount.scannedCodes_number <= 0:
            return generate_response("D004", '400')

    # Check user has not already scanned this code
    if len(discount.clients_id.filter(id=client.id)) > 0:
        return generate_response("D005", '400')


def get_client(request):
    user = getUserFromToken(request.headers["token"])
    client = Client.objects.get(user=user)

    return client


def get_client_id(id):
    client = Client.objects.get(id=id)

    return client


def get_owner(request):
    user = getUserFromToken(request.headers["token"])
    owner = Owner.objects.get(user=user)

    return owner


def validate_establishment_owner(establishment_id, owner):
    try:
        Establishment.objects.get(id=establishment_id, owner=owner)

    except Establishment.DoesNotExist:
        # Error: object does not exist, return 404
        return generate_response("E002", '400')


def get_valid_discounts(establishment_id):

    result_query = Q(establishment_id=establishment_id) & \
                   (Q(end_date__isnull=True, totalCodes_number__isnull=True) |
                    Q(end_date__isnull=True, totalCodes_number__isnull=False,
                      scannedCodes_number__lt=F('totalCodes_number')) |
                    Q(end_date__isnull=False, end_date__gt=timezone.now(), totalCodes_number__isnull=True) |
                    Q(end_date__isnull=False, end_date__gt=timezone.now(), totalCodes_number__isnull=False,
                      scannedCodes_number__lt=F('totalCodes_number'))
                    )

    discounts = Discount.objects.filter(result_query)

    return discounts


def generate_qr(token, host, establishment_id, discount_id, redirect_url):
    # Client
    user = getUserFromToken(token)
    client = Client.objects.get(user=user)

    # Code QR from hashed code

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )

    # TODO: Change url of view to be sent (talk with front)

    params = 'establishment_id=' + establishment_id + '&discount_id' + discount_id + '&client_id=' + str(client.id)

    api = 'login?' + str(params)

    if request.is_secure():
        http = "https://"
    else:
        http = "http://"

    qr.add_data(http + host + '/' + api)
    qr.make(fit=True)

    # QR to Bytes with PNG Format

    img = qr.make_image(fill_color='#e15f41', back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr
