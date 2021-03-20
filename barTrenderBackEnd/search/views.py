from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from authentication.decorators import token_required
from authentication.models import Establishment, Tag

class getEstablishments(APIView):
    @token_required('all')
    def post(self, request):

        #Get data from request
        filters = request.data["filters"]

        #Filter by zone if exist
        zone_filter = {} if not "zones" in filters else {'zone_enum__in': filters["zones"]}

        #Filter by beer
        beer_filter = {} if not "beers" in filters else {'tags__in': Tag.objects.filter(name__in = filters["beers"], type_enum="Bebida")}

        #Search establishments
        establishments = Establishment.objects.filter(**zone_filter).filter(**beer_filter).values('name_text', 'zone_enum', 'phone_number')

        response = {
            'establishments' : establishments
        }
        
        return Response(response, HTTP_200_OK)
