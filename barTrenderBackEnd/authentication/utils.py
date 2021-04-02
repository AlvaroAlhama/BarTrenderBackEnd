import jwt
from django.contrib.auth.models import User
import time
from authentication.models import Client, Owner
from django.conf import settings

HOURS = 1

def getRol(user):
    
    try:
        Client.objects.get(user=user)
        return "client"
    except:
        try:
            Owner.objects.get(user=user)
            return "owner"
        except:
            return None

def getToken(user, rol):

    #Expiration date of the token: Now + HOURS
    expiresIn = int(time.time()) + HOURS*3600

    payload = {
        "username": user.username,
        "rol": rol,
        "expiresIn": expiresIn
    }

    return jwt.encode(payload, settings.TOKEN_SECRET, algorithm="HS256"), expiresIn

def validateToken(token, rol):
    decoded = None
    try:
        decoded = jwt.decode(token, settings.TOKEN_SECRET, algorithms=["HS256"])
    except:
        return "Invalid Token"
        
    decodedExpiresIn = decoded["expiresIn"]
    decodedRol = decoded["rol"]

    if decodedExpiresIn < int(time.time()):
        return "Token Expired"
    if rol != "all":
        if decodedRol != rol:
            return "You dont have permission to access this site"

    return None

def getUserFromToken(token):
    decoded = jwt.decode(token, settings.TOKEN_SECRET, algorithms=["HS256"])
    username = decoded["username"]

    return User.objects.get(username=username)


