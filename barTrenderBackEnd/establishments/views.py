from rest_framework.views import APIView
from django.http import HttpResponse
from authentication.decorators import token_required
from authentication.utils import *
from .utils import *
from .serializers import *


class Discounts(APIView):

    def get(self, request, establishment_id):

        # globals params
        token = request.headers["token"]

        validations = validate_establishment(token, establishment_id)

        if validations is not None:
            return validations

        discounts = Discount.objects.filter(establishment_id=establishment_id)
        serializer = DiscountSerializer(discounts, many=True)

        body = {
            "discounts": serializer.data,
        }

        return Response(body, "200")


class DiscountsQR(APIView):
    @token_required("client")
    def get(self, request, establishment_id, discount_id):

        # globals params
        token = request.headers["token"]

        validations = validate_establishment(token, establishment_id)

        if validations is not None:
            return validations

        validations = validate_discount(token, establishment_id, discount_id)

        if validations is not None:
            return validations

        validations = validate_conditions(request, discount_id)
        if validations is not None:
            return validations

        # Return correct QR
        qr = generate_qr(token, establishment_id, discount_id)
        return HttpResponse(qr, status="200", content_type="image/png")


class Establishments(APIView):

    def post(self, request):

        # Get data from request
        filters = request.data["filters"]

        # Filter by zone if exist
        zone_filter = {} if not "zones" in filters else {'zone_enum__in': filters["zones"]}

        # Filter by beer
        beer_filter = {} if not "beers" in filters else {
            'tags__in': Tag.objects.filter(name__in=filters["beers"], type="Bebida")}

        # Search establishments
        establishments = Establishment.objects.filter(**zone_filter).filter(**beer_filter).values(
            'name_text', 'zone_enum', 'phone_number')

        response = {
            'establishments': establishments
        }

        return Response(response, "200")
