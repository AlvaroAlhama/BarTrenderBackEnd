from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from authentication.decorators import token_required, apikey_required
from authentication.utils import *
from .utils import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
import pytz
import datetime
from django.db.models import Q, F
from barTrenderBackEnd.errors import generate_response
from payments.models import Payment
import requests

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
        endDate = datetime.datetime.fromtimestamp(discount["endDate"], pytz.timezone('Europe/Madrid')) if "endDate" in discount else None
        #Generate the discount
        discount = Discount.objects.create(name_text=discount["name"], description_text=discount["description"], cost_number=discount["cost"], totalCodes_number=totalCodes,
                                scannedCodes_number=0, initial_date=datetime.datetime.fromtimestamp(discount["initialDate"], pytz.timezone('Europe/Madrid')), end_date=endDate, 
                                establishment_id=Establishment.objects.get(id=establishment_id))

        # Create Payment associated to
        Payment.objects.create(pay_date=discount.initial_date + datetime.timedelta(days=30), scanned_number=0, discount_id=discount)

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
        endDate = datetime.datetime.fromtimestamp(discount["endDate"], pytz.timezone('Europe/Madrid')) if "endDate" in discount else None
        scannedCodes = discount["scannedCodes"] if "scannedCodes" in discount else 0

        #Update the discount
        discount_stored.name_text = discount["name"]
        discount_stored.description_text = discount["description"]
        discount_stored.cost_number = discount["cost"]
        discount_stored.totalCodes_number = totalCodes
        discount_stored.scannedCodes_number = scannedCodes
        if discount["initialDate"] > time.time():
            discount_stored.initial_date = datetime.datetime.fromtimestamp(discount["initialDate"], pytz.timezone('Europe/Madrid'))
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

        return Response({"msg": "The discount has been deleted"}, 200)


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

        # Update Payment

        payment = Payment.objects.get(discount_id=discount.id)

        payment.scanned_number += 1
        payment.save()

        return Response({"msg": "Success Scanning the QR. Discount applied!"}, "200")


class Establishments(APIView):

    @token_required("owner")
    def post(self, request):

        try:
            name_text = request.data['name_text']
            cif_text = request.data['cif_text']
            phone_number = request.data['phone_number']
            zone_enum = request.data['zone_enum']
            tags = request.data['tags']
            street_text = request.data['street_text']
            number_text = request.data['number_text']
            locality_text = request.data['locality_text']

        except Exception as e:
            return generate_response("Z001", 400)

        tags_list = []
        for tag in tags:
            try:
                tags_list.append(Tag.objects.get(name=tag))
            except Exception as e:
                return generate_response("E003", "400")

        try:
            desc_text = request.data['desc_text'].strip()
        except Exception as e:
            desc_text = None

        try:
            image_url = request.data['image_url'].strip()
        except Exception as e:
            image_url = None

        establishment = Establishment(
            name_text=name_text,
            desc_text=desc_text,
            cif_text=cif_text,
            phone_number=phone_number,
            zone_enum=zone_enum,
            owner=get_owner(request),
            street_text=street_text,
            number_text=number_text,
            locality_text=locality_text,
            image_url=image_url
        )

        try:
            establishment.full_clean()
        except ValidationError as e:
            key = str(list(e.message_dict.keys())[0])
            err_msg = e.message_dict[key][0]
            return Response({'error': 'V001: Error de validacion: ' + err_msg + ' (' + key + ')'}, "400")

        establishment.save()

        establishment.tags.add(*tags_list)

        return Response({"msg": "Success Creating Establishment"}, "200")

    @token_required("owner")
    def put(self, request, establishment_id):

        valid = validate_establishment(establishment_id)
        if valid is not None:
            return valid

        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None:
            return valid

        try:
            name_text = request.data['name_text']
            phone_number = request.data['phone_number']
            zone_enum = request.data['zone_enum']
            tags = request.data['tags']
            desc_text = request.data['desc_text']
            street_text = request.data['street_text']
            number_text = request.data['number_text']
            locality_text = request.data['locality_text']
            image_url = request.data['image_url']
        except Exception as e:
            return generate_response("Z001", 400)

        tags_list = []
        for tag in tags:
            try:
                tags_list.append(Tag.objects.get(name=tag))
            except Exception as e:
                return generate_response("E003", "400")

        establishment = Establishment.objects.get(id=establishment_id)

        establishment.name_text = name_text
        establishment.desc_text = desc_text
        establishment.phone_number = phone_number
        establishment.zone_enum = zone_enum
        establishment.street_text = street_text
        establishment.number_text = number_text
        establishment.locality_text = locality_text
        establishment.image_url = image_url

        try:
            establishment.full_clean()
        except ValidationError as e:
            msg = []
            for err in e.message_dict:
                msg.append(e.message_dict[err])

            error_msg = str(msg[0]).replace('[', '').replace(']', '').replace("'", '')
            return Response({'error': 'V001: Error de validacion: ' + error_msg}, "400")

        establishment.tags.set(tags_list)

        establishment.save()

        return Response({"msg": "Success Updating Establishment"}, "200")

    @token_required("owner")
    def delete(self, request, establishment_id):

        valid = validate_establishment(establishment_id)
        if valid is not None:
            return valid

        valid = validate_establishment_owner(establishment_id, get_owner(request))
        if valid is not None:
            return valid

        http = "http"
        if request.is_secure():
            http = "https"

        host = http + "://" + request.get_host()
        url = host + "/v1/payments/establishments/" + str(establishment_id) + "/calculate"
        headers = {
            "token": request.headers["token"],
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return generate_response("API003", 400)
        else:
            data = json.loads(response.content)

        if data['total'] != 0:
            return generate_response("E004", 400)

        establishment = Establishment.objects.get(id=establishment_id)
        establishment.delete()

        return Response({"msg": "Success Deleting Establishment"}, "200")


class FilterEstablishments(APIView):
    @apikey_required
    def post(self, request):

        # Get data from request
        try:
            filters = request.data["filters"]
        except:
            return generate_response("Z001", 400)

        # save the search for statistics
        save_search(filters)
        
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

        # Filter by name
        name_filter = {} if not "name" in filters else {
            'name_text__icontains': str(filters['name']).lower()}

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
                **zone_filter).filter(**beer_filter).filter(**leisure_filter).filter(**style_filter).filter(**circle_filter).filter(**name_filter).filter(discount_filter).filter(verified_bool=True)    
        else:
            establishments = Establishment.objects.filter(
                **zone_filter).filter(**beer_filter).filter(**leisure_filter).filter(**style_filter).filter(**circle_filter).filter(**name_filter).filter(verified_bool=True)

        establishments = establishments.distinct()

        response = []

        for e in establishments:
            tags = e.tags.all().values("name", "type")
            response.append({
                'id': e.id,
                'name': e.name_text,
                'phone': e.phone_number,
                'zone': e.zone_enum, 
                'street': e.street_text,
                'number': e.number_text,
                'locality': e.locality_text,
                'image': e.image_url,
                'tags': tags,
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
                "initialDate": int(datetime.datetime.timestamp(d.initial_date)),
                "endDate": None if d.end_date == None else int(datetime.datetime.timestamp(d.end_date))
            })

        response = {
            "establishment": {
                'id': establishment.id,
                'name': establishment.name_text,
                'phone': establishment.phone_number,
                'zone': establishment.zone_enum,
                'street': establishment.street_text,
                'number': establishment.number_text,
                'locality': establishment.locality_text,
                'image': establishment.image_url,
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

