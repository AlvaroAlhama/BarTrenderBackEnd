from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView

class getTestMsg(APIView):
    def get(self, request):

        context = {
            'msg': 'hello world'
        }

        return Response(context, HTTP_200_OK)