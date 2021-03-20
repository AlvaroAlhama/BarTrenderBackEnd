from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
import json
from authentication.models import Client, Owner
from authentication.utils import getToken, getRol
from authentication.decorators import token_required, apikey_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class login(APIView):
    @apikey_required
    def post(self, request):
        
        #Get data from request
        body = json.loads(request.body)
        email = body["email"]
        password = body["password"]

        #Get the user if exists
        user = authenticate(username=email, password=password)
        if user is None:
            return Response({"error": "Email or password incorrect"}, HTTP_401_UNAUTHORIZED)
        
        rol = getRol(user)
        if rol == None:
            return Response({"error": "Sorry my friend"}, HTTP_401_UNAUTHORIZED)

        #Generate the token with the correct claims
        token, expiresIn = getToken(user, rol)

        response = {
            'token': token,
            'expiresIn': expiresIn,
            'rol': rol
        }

        return Response(response, HTTP_200_OK)

class testAll(APIView):
    @token_required('all')
    def get(self, request):
        return Response("Has accedido!", HTTP_200_OK)

class testOwner(APIView):
    @token_required('owner')
    def get(self, request):
        return Response("Has accedido, owner!", HTTP_200_OK)