from rest_framework.views import APIView
from django.http import HttpResponse
from authentication.decorators import token_required
from authentication.utils import *
from .utils import *


class Discounts(APIView):
    @token_required("client")
    def get(self, request, establishment_id, discount_id):

        # globals params
        token = request.headers["token"]

        validations = validate_params(token, establishment_id, discount_id)

        if validations is not None:
            return validations

        validations = validate_conditions(request, discount_id)
        if validations is not None:
            return validations

        # Return correct QR

        qr = generate_qr(token, establishment_id, discount_id)
        return HttpResponse(qr, status="200", content_type="image/png")
