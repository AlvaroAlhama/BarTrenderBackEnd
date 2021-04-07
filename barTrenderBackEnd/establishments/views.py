from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from authentication.decorators import token_required, apikey_required
from authentication.utils import *
from .utils import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
import pytz
from datetime import datetime
from django.db.models import Q, F
from barTrenderBackEnd.errors import generate_response


class Discounts(APIView):
    @apikey_required
    def get(self, request, establishment_id):
        
        # globals params

        validations = validate_establishment(establishment_id)
        if validations is not None:
            return validations

        paginator = PageNumberPagination()
        paginator.page_size = 7
        print(request.GET['all'])
        if request.GET['all'] is None or request.GET['all'] == "False":
            discounts = get_valid_discounts(establishment_id, False)
        else:
            discounts = get_valid_discounts(establishment_id, True)

        if discounts is None:
            return generate_response("D022", 400)

        context = paginator.paginate_queryset(discounts, request)
        serializer = DiscountSerializer(context, many=True)

        return paginator.get_paginated_response(serializer.data)

    @token_required("owner")
    def post(self, request, establishment_id):
        #Validation
        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None: return valid

        try: discount = request.data
        except: return generate_response("Z001", 400)

        valid = validate_discount_request(discount)
        if valid is not None: return valid

        totalCodes = discount["totalCodes"] if "totalCodes" in discount else None
        endDate = datetime.fromtimestamp(discount["endDate"], pytz.timezone('Europe/Madrid')) if "endDate" in discount else None
        #Generate the discount
        Discount.objects.create(name_text=discount["name"], description_text=discount["description"], cost_number=discount["cost"], totalCodes_number=totalCodes,
                                scannedCodes_number=0, initial_date=datetime.fromtimestamp(discount["initialDate"], pytz.timezone('Europe/Madrid')), end_date=endDate, 
                                establishment_id=Establishment.objects.get(id=establishment_id))

        return Response({"msg":"The discount has been created"}, 201)

    @token_required("owner")
    def put(self, request, establishment_id, discount_id):
        #Validation
        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None: return valid

        valid = validate_discount(establishment_id, discount_id)
        if valid is not None: return valid

        try: discount = request.data
        except: return generate_response("Z001", 400)

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

        return Response({"msg":"The discount has been updated"}, 200)
    
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

        return Response({"msg":"The discount has been deleted"}, 200)


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
        qr = generate_qr(request, token, request.GET['custom_host'], establishment_id, discount_id)
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

        return Response({"msg": "Success Scanning the QR. Discount applied!"}, "200")


class Establishments(APIView):
    @apikey_required
    def post(self, request):

        # Get data from request
        try:
            filters = request.data["filters"]
        except:
            return generate_response("Z001", 400)

        # Filter by zone if exist

        zone_filter = {} if not "Zona" in filters else {'zone_enum__in': filters["Zona"]}

        # Filter by beer
        beer_filter = {} if not "Bebida" in filters else {
            'tags__in': Tag.objects.filter(name__in=filters["Bebida"], type="Bebida")}
        
        # Filter by leisure
        leisure_filter = {} if not "Ocio" in filters else {
            'tags__in': Tag.objects.filter(name__in=filters["Ocio"], type="Ocio")}

        # Filter by style
        style_filter = {} if not "Estilo" in filters else {
            'tags__in': Tag.objects.filter(name__in=filters["Estilo"], type="Estilo")}

        # Filter by circle
        circle_filter = {} if not "Ambiente" in filters else {
            'tags__in': Tag.objects.filter(name__in=filters["Ambiente"], type="Ambiente")}

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
                **zone_filter).filter(**beer_filter).filter(**leisure_filter).filter(**style_filter).filter(**circle_filter).filter(discount_filter)    
        else:
            establishments = Establishment.objects.filter(
                **zone_filter).filter(**beer_filter).filter(**leisure_filter).filter(**style_filter).filter(**circle_filter)

        establishments = establishments.distinct()

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


class Establishment_By_EstablishmentId(APIView):

    @token_required('owner')
    def get(self, request, establishment_id):
        
        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None: return valid

        establishment = Establishment.objects.get(id=establishment_id)
        discounts = Discount.objects.filter(establishment_id=establishment)
        
        ds = []

        for d in discounts:
            ds.append({
                "id": d.id,
                "name": d.name_text,
                "description": d.description_text,
                "cost": d.cost_number,
                "totalCodes": d.totalCodes_number,
                "scannedCodes": d.scannedCodes_number,
                "initialDate": int(datetime.timestamp(d.initial_date)),
                "endDate": None if d.end_date == None else int(datetime.timestamp(d.end_date))
            })

        response = {
            "establishment": {
                'id': establishment.id,
                'name': establishment.name_text,
                'phone': establishment.phone_number,
                'zone': establishment.zone_enum, 
                'tags': establishment.tags.all().values("name", "type")
            },
            "discounts": ds
        }

        return Response(response, 200)


class EstablishmentsByOwner(APIView):

    @token_required("owner")
    def get(self, request):

        try:
            owner = get_owner(request)
        except Owner.DoesNotExist:
            return generate_response("A002", '404')

        establishments = Establishment.objects.filter(owner=owner.id)
        serializer = EstablishmentSerializer(establishments, many=True)

        return Response(serializer.data, 200)

class Tags(APIView):
    @apikey_required
    def get(self, request):

        tags = Tag.objects.all().values('name', 'type')

        zones = Establishment.objects.all().values('zone_enum').distinct()

        response = {'tags': []}

        for tag in tags:
            response['tags'].append({'name': tag['name'], 'type': tag['type']})

        for zone in zones:
            response['tags'].append({'name': zone['zone_enum'], 'type': 'Zona'})
     
        return Response(response, 200)

