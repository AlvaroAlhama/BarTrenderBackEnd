from rest_framework.response import Response
from rest_framework.views import APIView
import qrcode
import hashlib
import datetime
import io
from django.http import HttpResponse
from authentication.decorators import token_required
from authentication.utils import *
from .models import *

# ERROR MSG

errors = {
    "login_400": "Could not validate session. Please retry later!",
    "establishment_404": "Could not find Establishment from Establishment Id: {v}.",
    "discount_400": "Establishment Id: {v} does not correspond with Discount Id: {v}.",
    "discount_403": "Not allowed :S",
    "discount_404": "Could not find Discount from Discount Id: {v}.",
}


def generate_response(error_msg, *variables):

    status = error_msg.split('_')[1]

    formatted_error_msg = str(errors[error_msg])
    for variable in variables:
        formatted_error_msg = formatted_error_msg.replace('{v}', str(variable), 1)

    return Response(data=formatted_error_msg, status=status)


def validate_params(token, establishment_id, discount_id):
    # Validate User
    if validateToken(token, "client") == None:
        return generate_response("login_400")

    # Validate Establishment
    try:
        Establishment.objects.get(id=establishment_id)
    except Establishment.DoesNotExist:
        # Error: object does not exist, return 404
        return generate_response("establishment_404", establishment_id)

    # Validate Discount
    try:
        discount = Discount.objects.get(id=discount_id)

        if discount.establishment_id.id != establishment_id:
            # Return error 400: Bad Request
            return generate_response("discount_400", establishment_id, discount_id)
    except Discount.DoesNotExist:
        # Error: object does not exist, return 404
        return generate_response("discount_404", discount_id)


def validate_conditions(request, discount_id):

    # User
    user = getUserFromToken(request.headers["token"])
    client = Client.objects.get(user=user)
    discount = Discount.objects.get(id=discount_id)

    # Check if the code is going to be scanned in time
    if discount.end_date != None:
        if datetime.datetime.now().date() > discount.end_date:
            return False

    # Check there are available QR Codes when they are limited
    if discount.totalCodes_number != None:
        if discount.totalCodes_number - discount.scannedCodes_number <= 0:
            return False

    # Check user has not already scanned this code

    if len(discount.clients_id.filter(id=client.id)) > 0:
        return False

    return True


def generate_qr(token, establishment_id, discount_id):
    # HashInfo and generate code
    scan_datetime = datetime.datetime.now()

    coded_str = str.encode("user_token" + str(establishment_id) + str(discount_id) + str(scan_datetime))
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


class Discounts(APIView):

    def get(self, request, establishment_id, discount_id):

        # Check for:
        #   - token is valid and belongs to a real user
        #   - establishment_id belongs to a registered establishment
        #   - discount_id is a registered discount and belongs to the named establishment

        # globals params
        token = request.headers["token"]

        if not validate_params(token, establishment_id, discount_id):
            return generate_response("discount_400")

        if not validate_conditions(request, discount_id):
            return generate_response("discount_403")

        # Return correct QR

        qr = generate_qr(token, establishment_id, discount_id)
        return HttpResponse(qr, status="200", content_type="image/png")
