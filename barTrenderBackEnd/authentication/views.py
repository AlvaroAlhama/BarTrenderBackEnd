from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from authentication.models import Client, Owner
from authentication.utils import getToken, getRol
from authentication.decorators import token_required, apikey_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from barTrenderBackEnd.errors import generate_response


class login(APIView):
    @apikey_required
    def post(self, request):
        
        #Get data from request
        try:
            body = request.data
            email = body["email"]
            password = body["password"]
        except:
            return generate_response("Z001", 401)

        #Get the user if exists
        user = authenticate(username=email, password=password)
        if user is None:
            return generate_response("A009", 401)
        
        rol = getRol(user)
        if rol == None:
            return generate_response("A010", 401)

        #Generate the token with the correct claims
        token, expiresIn = getToken(user, rol)

        response = {
            'token': token,
            'expiresIn': expiresIn,
            'rol': rol
        }

        return Response(response, 200)