from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from authentication.decorators import token_required
from authentication.utils import *
from .utils import *
from .serializers import *


class Discounts(APIView):

    def get(self, request, establishment_id):

        # globals params

        validations = validate_establishment(establishment_id)
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
    def post(self, request, establishment_id, discount_id):

        # globals params
        token = request.headers["token"]
        redirect_url = request.data["redirect_url"]

        validations = validate_establishment(establishment_id)

        if validations is not None:
            return validations

        validations = validate_discount(establishment_id, discount_id)

        if validations is not None:
            return validations

        validations = validate_conditions(get_client(request), discount_id)
        if validations is not None:
            return validations

        # Return correct QR
        qr = generate_qr(token, request.get_host(), establishment_id, discount_id, redirect_url)
        return HttpResponse(qr, status="200", content_type="image/png")


class ScanDiscount(APIView):
    @token_required("owner")
    def get(self, request, establishment_id, discount_id):

        # globals params

        if not request.is_secure():
            redirect_url = 'http://' + request.GET["redirect_url"]
        else:
            redirect_url = 'https://' + request.GET["redirect_url"]

        try:
            owner = get_owner(request)
        except Owner.DoesNotExist:
            return generate_response("A002", '404')

        # Check owner owns establishment
        validations = validate_establishment_owner(establishment_id, owner)
        if validations is not None:
            return validations

        # Check Discount is valid
        validations = validate_discount(establishment_id, discount_id)
        if validations is not None:
            return validations

        # Get Client
        try:
            client = get_client_id(request.GET["client_id"])
        except Client.DoesNotExist:
            return generate_response("A001", "404")

        validations = validate_conditions(client, discount_id)
        if validations is not None:
            return validations

        # Discount logic

        discount = Discount.objects.get(id=discount_id)
        discount.scannedCodes_number += 1

        discount.clients_id.add(client)
        discount.save()

        return HttpResponseRedirect(redirect_url)


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
            'id', 'name_text', 'zone_enum', 'phone_number')

        response = {
            'establishments': establishments
        }

        return Response(response, "200")
