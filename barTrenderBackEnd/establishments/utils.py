from rest_framework.response import Response
import qrcode
import hashlib
import datetime
import io
from authentication.utils import *
from .models import *
from django.utils import timezone


# ERROR MSG

errors = {
    'E001': 'Establecimiento no existe',
    'D001': 'Descuento no existe',
    'D002': 'Descuento no pertenece al establicimiento',
    'D003': 'El descuento ha expirado',
    'D004': 'No quedan descuentos disponibles',
    'D005': 'Descuento ya escaneado por usuario',
}

# TODO: Create function to validate CIF when creating Establishments and Validate Dates when creating Discounts


def generate_response(code, status):

    body = {
        'error': str(code) + ": " + errors[code]
    }

    return Response(body, status)


def validate_discount(token, establishment_id, discount_id):

    # Validate Discount
    try:
        discount = Discount.objects.get(id=discount_id)

        if discount.establishment_id.id != establishment_id:
            # Return error 400: Bad Request
            return generate_response("D002", '400')
    except Discount.DoesNotExist:
        # Error: object does not exist, return 404
        return generate_response("D001", '404')


def validate_establishment(token, establishment_id):

    # Validate Establishment
    try:
        Establishment.objects.get(id=establishment_id)
    except Establishment.DoesNotExist:
        # Error: object does not exist, return 404
        return generate_response("E001", '404')


def validate_conditions(request, discount_id):

    # User
    user = getUserFromToken(request.headers["token"])
    client = Client.objects.get(user=user)
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


def generate_qr(token, establishment_id, discount_id):
    # HashInfo and generate code
    scan_datetime = datetime.datetime.now()

    coded_str = str.encode(token + str(establishment_id) + str(discount_id) + str(scan_datetime))
    hash_string = str(hashlib.md5(coded_str).hexdigest())

    # Code QR from hashed code

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )

    # TODO: Change url of view to be sent (talk with front)
    qr.add_data('http://localhost:8000/code?qr_scaned=' + hash_string)
    qr.make(fit=True)

    # QR to Bytes with PNG Format

    img = qr.make_image(fill_color='#e15f41', back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr
