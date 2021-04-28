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
from google.oauth2 import id_token
from google.auth.transport import requests
import os


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

class IsPremium(APIView):
    @token_required('owner')
    def get(self, request):
        user = getUserFromToken(request.headers['token'])
        owner = Owner.objects.get(user=user)

        premiumUntil = None
        premiumRemainingDays = None
        
        if owner.premium and owner.premium_end_date < datetime.date.today():
            owner.premium = False
            owner.save()

        if owner.premium:
            premiumUntil = int(time.mktime(datetime.datetime.strptime(str(owner.premium_end_date), "%Y-%m-%d").timetuple()))
            premiumRemainingDays = (owner.premium_end_date - datetime.date.today()).days

        
        response = {
                "isPremium": owner.premium,
                "premiumUntil": premiumUntil,
                "premiumRemainingDays": premiumRemainingDays,
        }

        return Response(response, 200)

class UserInformation(APIView):
    @token_required('all')
    def get(self, request):

        user  = getUserFromToken(request.headers['token'])

        rol = getRol(user)

        if rol == 'client':
            client = Client.objects.filter(user=user).get()
            response = {
                "email": user.username,
                "name": user.first_name,
                "surname": user.last_name,
                "birthday": int(datetime.datetime.strptime(str(client.birthday), "%Y-%m-%d").timestamp())
            }
        else:
            owner = Owner.objects.filter(user=user).get()
            response = {
                "email": user.username,
                "name": user.first_name,
                "surname": user.last_name,
                "phone": owner.phone
            }

        return Response(response, 200)

    @token_required('all')
    def put(self, request):

        user  = getUserFromToken(request.headers['token'])

        rol = getRol(user)

        valid = valid_data_update(request.data, rol)

        if valid != None:
            return generate_response(valid, 400)

        valid = valid_user_update(user, request.data)

        if valid != None:
            return generate_response(valid, 400)

        user.username = request.data['email']
        if "password" in request.data:
            user.set_password(request.data["password"])
        user.first_name = request.data['name']
        user.last_name = request.data['surname']
        user.save()


        if rol == 'client':
            client = Client.objects.filter(user=user).get()
            client.birthday = datetime.date.fromtimestamp(request.data['birthday'])
            client.save()
        else:
            owner = Owner.objects.filter(user=user).get()
            owner.phone = request.data['phone']
            owner.save()

        token, expiresIn = getToken(user, rol)

        premium = isPremium(user, rol)

        response = {
            'token': token,
            'expiresIn': expiresIn,
            'rol': rol,
            'premium': premium,
            'msg': 'Se ha actualizado el usuario correctamente'
        }

        return Response(response, 200)


class GoogleLogin(APIView):
    @apikey_required
    def post(self, request):

        token = request.data["user"]["token"]
        clientId = os.environ["GOOGLE_CLIENT_ID"]

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), clientId)
        except Exception as e:
            return Response({"error": str(e)}, 400)

        # Check Validity of token
        if request.data["user"]["email"] == idinfo["email"] and idinfo["email_verified"]:

            try:
                user = User.objects.get(username=idinfo["email"])
            except User.DoesNotExist:
                user = None

            if user is not None:

                rol = getRol(user)

                if rol is None:
                    return generate_response("A010", 401)

                # Generate the token with the correct claims
                token, expiresIn = getToken(user, rol)

                premium = isPremium(user, rol)

                response = {
                    'token': token,
                    'expiresIn': expiresIn,
                    'rol': rol,
                    'premium': premium
                }

                return Response(response, 200)

            else:

                # Register user
                if request.data["rol"] == "client":

                    fake_body = {
                        "email": idinfo["email"],
                        "password": None,
                        "birthday": request.data["user"]["birthday"],
                        "rol": "client"
                    }

                    # Validate the data
                    valid = validateSignupDataGoogle(fake_body)
                    if valid is not None:
                        return generate_response(valid, 401)

                    user, err = createUser(fake_body)

                    if err is not None:
                        return generate_response(err, 400)

                    # Generate the token
                    token, expiresIn = getToken(user, fake_body["rol"])

                    response = {
                        'token': token,
                        'expiresIn': expiresIn,
                        'rol': fake_body["rol"],
                        'email': fake_body["email"],
                        'msg': 'Usuario creado correctamente',
                        'premium': False
                    }
                    return Response(response, 200)

                elif request.data["rol"] == "owner":

                    fake_body = {
                        "email": idinfo["email"],
                        "password": None,
                        "phone": request.data["user"]["phone"],
                        "rol": "owner"
                    }

                    # Validate the data
                    valid = validateSignupDataGoogle(fake_body)
                    if valid is not None:
                        return generate_response(valid, 401)

                    user, err = createUser(fake_body)

                    if err is not None:
                        return generate_response(err, 400)

                    # Generate the token
                    token, expiresIn = getToken(user, fake_body["rol"])

                    response = {
                        'token': token,
                        'expiresIn': expiresIn,
                        'rol': fake_body["rol"],
                        'email': fake_body["email"],
                        'msg': 'Usuario creado correctamente',
                        'premium': False
                    }

                    return Response(response, 200)

        return generate_response("A019", 400)
