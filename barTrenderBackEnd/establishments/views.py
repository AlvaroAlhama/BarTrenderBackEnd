from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from authentication.decorators import token_required, apikey_required
from authentication.utils import *
from .utils import *
from .serializers import *
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from django.utils import timezone
from django.db.models import Q, F


class Discounts(APIView):
    @apikey_required
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
    @apikey_required
    def post(self, request):

        # Get data from request
        try:
            filters = request.data["filters"]
        except:
            return Response({"error": "Incorrect Payload"}, HTTP_401_UNAUTHORIZED)

        # Filter by zone if exist
        zone_filter = {} if not "zones" in filters else {'zone_enum__in': filters["zones"]}

        # Filter by beer
        beer_filter = {} if not "beers" in filters else {
            'tags__in': Tag.objects.filter(name__in=filters["beers"], type="Bebida")}
        
        # Filter by leisure
        leisure_filter = {} if not "leisures" in filters else {
            'tags__in': Tag.objects.filter(name__in=filters["leisures"], type="Ocio")}

        # Filter by Discount:
        # Get all the establishment that have discounts, filter the establishment by this ids
        discount_filter = ''
        if "discounts" in filters:
            if filters["discounts"]:
                discount_filter = (Q(discount__end_date__isnull=True, discount__initial_date__lt=timezone.now(), 
                    discount__totalCodes_number__isnull=True) | Q(discount__end_date__isnull=True,
                    discount__initial_date__lt=timezone.now(), discount__totalCodes_number__isnull=False, 
                    discount__scannedCodes_number__lt=F('discount__totalCodes_number')) | Q(discount__end_date__isnull=False, 
                    discount__end_date__gt=timezone.now(), discount__initial_date__lt=timezone.now(), discount__totalCodes_number__isnull=True) |
                    Q(discount__end_date__isnull=False, discount__end_date__gt=timezone.now(), discount__initial_date__lt=timezone.now(), 
                    discount__totalCodes_number__isnull=False, discount__scannedCodes_number__lt=F('discount__totalCodes_number')))
        

        # Search establishments
        if discount_filter != '':
            establishments = Establishment.objects.filter(
                **zone_filter).filter(**beer_filter).filter(**leisure_filter).filter(discount_filter)    
        else:
            establishments = Establishment.objects.filter(
                **zone_filter).filter(**beer_filter).filter(**leisure_filter)

        response = []

        for e in establishments:
            tags = e.tags.all().values("name", "type")
            response.append({
                'name': e.name_text,
                'phone': e.phone_number,
                'zone': e.zone_enum, 
                'tags': tags
            })

        return Response(response, "200")
