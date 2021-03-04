from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
import qrcode
import hashlib
import datetime
import io
from django.http import HttpResponse

class getTestMsg(APIView):
    def get(self, request):

        ######## Sample Data

        username = "enrreigut"
        cod_descuento = 89859
        fecha = datetime.datetime.now()

        ############################

        coded_str = str.encode(str(username+str(cod_descuento)+str(fecha)))
        hash_string = str(hashlib.md5(coded_str).hexdigest())

        ######## Code QR

        qr = qrcode.QRCode(
            version = 1,
            error_correction= qrcode.constants.ERROR_CORRECT_Q,
            box_size= 10,
            border= 4,
        )

        qr.add_data('http://localhost:8000/code?qr_scaned='+hash_string)
        qr.make(fit=True)

        # QR to Bytes with PNG Format

        img = qr.make_image(fill_color='black', back_color="white")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        ############################

        return HttpResponse(img_byte_arr, content_type="image/png")