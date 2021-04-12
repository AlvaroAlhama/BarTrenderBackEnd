from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from authentication.models import Client, Owner
from authentication.utils import *
from authentication.decorators import token_required, apikey_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from barTrenderBackEnd.errors import generate_response


class login(APIView):
    @apikey_required
    def post(self, request):
        
        #Get data from request
        try:
            body = json.loads(request.body)
        except:
            return generate_response("Z001", 401)

        if 'email' not in body or 'password' not in body:
            return generate_response("Z001", 401)

        email = body["email"]
        password = body["password"]

        #Get the user if exists
        user = authenticate(username=email, password=password)
        if user is None:
            return generate_response("A009", 401)
        
        rol = getRol(user)
        if rol == None:
            return generate_response("A010", 401)

        #Generate the token with the correct claims
        token, expiresIn = getToken(user, rol)

        premium = isPremium(user, rol)

        response = {
            'token': token,
            'expiresIn': expiresIn,
            'rol': rol,
            'premium': premium
        }

        return Response(response, 200)

class signup(APIView):
    @apikey_required
    def post(self, request):
        
        #Get data from request
        body, err = getSignupData(request)
        if err != None: return generate_response(err, 401)

        #Validate the data
        valid = validateSignupData(body)
        if valid is not None: return generate_response(valid,401)
        
        #Create the user
        user, err = createUser(body)
        if err is not None: return generate_response(err, 400)

        #Generate the token
        token, expiresIn = getToken(user, body["rol"])

        response = {
            'token': token,
            'expiresIn': expiresIn,
            'rol': body["rol"],
            'email': body["email"],
            'msg': 'Usuario creado correctamente',
            'premium': False
        }

        return Response(response,200)

class SetPremium(APIView):
    @token_required('owner')
    def post(self, request):
        
        #Get data from request
        try:
            body = request.body
        except:
            return generate_response("Z001", 400)

        error_code = setpremium(request.headers['token'], request.data['order_id'], request.data['create_time'])
        if error_code != None: return generate_response(error_code, 400)
        
        response = {
            'msg': 'Premium pagado'
        }

        return Response(response,200)