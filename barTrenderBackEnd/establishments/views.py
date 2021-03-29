from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from authentication.decorators import token_required, apikey_required
from authentication.utils import *
from .utils import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from django.utils import timezone
import pytz
from datetime import datetime
from django.db.models import Q, F


class Discounts(APIView):
    @apikey_required
    def get(self, request, establishment_id):

        # globals params

        validations = validate_establishment(establishment_id)
        if validations is not None:
            return validations

        paginator = PageNumberPagination()
        paginator.page_size = 7

        if request.GET['all'] is None or request.GET['all'] == "False":
            discounts = get_valid_discounts(establishment_id, False)
        else:
            discounts = get_valid_discounts(establishment_id, True)

        if discounts is None:
            return Response({"No valid query"}, '400')

        context = paginator.paginate_queryset(discounts, request)
        serializer = DiscountSerializer(context, many=True)

        return paginator.get_paginated_response(serializer.data)

    @token_required("owner")
    def post(self, request, establishment_id):
        #Validation
        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None: return valid

        try: discount = request.data
        except: return Response({"error": "Incorrect Payload"}, HTTP_401_UNAUTHORIZED)

        valid = validate_discount_request(discount)
        if valid is not None: return valid

        totalCodes = discount["totalCodes"] if "totalCodes" in discount else None
        endDate = datetime.fromtimestamp(discount["endDate"], pytz.timezone('Europe/Madrid')) if "endDate" in discount else None
        #Generate the discount
        Discount.objects.create(name_text=discount["name"], description_text=discount["description"], cost_number=discount["cost"], totalCodes_number=totalCodes,
                                scannedCodes_number=0, initial_date=datetime.fromtimestamp(discount["initialDate"], pytz.timezone('Europe/Madrid')), end_date=endDate, 
                                establishment_id=Establishment.objects.get(id=establishment_id))

        return Response({"msg":"The discount has been created"}, HTTP_201_CREATED)

    @token_required("owner")
    def put(self, request, establishment_id, discount_id):
        #Validation
        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None: return valid

        valid = validate_discount(establishment_id, discount_id)
        if valid is not None: return valid

        try: discount = request.data
        except: return Response({"error": "Incorrect Payload"}, HTTP_401_UNAUTHORIZED)

        valid, discount_stored = validate_discount_update(discount, discount_id)
        if valid is not None: return valid

        totalCodes = discount["totalCodes"] if "totalCodes" in discount else None
        endDate = datetime.fromtimestamp(discount["endDate"], pytz.timezone('Europe/Madrid')) if "endDate" in discount else None
        scannedCodes = discount["scannedCodes"] if "scannedCodes" in discount else 0

        #Update the discount
        discount_stored.name_text = discount["name"]
        discount_stored.description_text = discount["description"]
        discount_stored.cost_number = discount["cost"]
        discount_stored.totalCodes_number = totalCodes
        discount_stored.scannedCodes_number = scannedCodes
        if discount["initialDate"] > time.time():
            discount_stored.initial_date = datetime.fromtimestamp(discount["initialDate"], pytz.timezone('Europe/Madrid'))
        discount_stored.end_date = endDate
        discount_stored.establishment_id = Establishment.objects.get(id=establishment_id)
        discount_stored.update()

        return Response({"msg":"The discount has been updated"}, HTTP_200_OK)
    
    @token_required("owner")
    def delete(self, request, establishment_id, discount_id):
        #Validation
        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None: return valid

        valid = validate_discount(establishment_id, discount_id)
        if valid is not None: return valid

        valid, discount = validate_discount_delete(discount_id)
        if valid is not None: return valid
        #Delete discount
        discount.delete()

        return Response({"msg":"The discount has been deleted"}, HTTP_200_OK)

class DiscountsQR(APIView):
    @token_required("client")
    def get(self, request, establishment_id, discount_id):

        # globals params
        token = request.headers["token"]

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
        qr = generate_qr(request, token, request.get_host(), establishment_id, discount_id)
        return HttpResponse(qr, status="200", content_type="image/png")


class ScanDiscount(APIView):
    @token_required("owner")
    def get(self, request, establishment_id, discount_id, client_id):

        # globals params
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
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return generate_response("A001", "404")

        validations = validate_conditions(client, discount_id)
        if validations is not None:
            return validations

        # Discount logic

        discount = Discount.objects.get(id=discount_id)
        discount.scannedCodes_number += 1

        discount.update()
        discount.clients_id.add(client)

        return Response({"Success Scanning the QR. Discount applied!"}, "200")


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
                'id': e.id,
                'name': e.name_text,
                'phone': e.phone_number,
                'zone': e.zone_enum, 
                'tags': tags
            })

        return Response(response, "200")
