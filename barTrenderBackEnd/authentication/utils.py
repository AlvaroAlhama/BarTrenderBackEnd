import jwt
from django.contrib.auth.models import User
import time
from authentication.models import Client, Owner

SECRET = "secreto"
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

    return jwt.encode(payload, SECRET, algorithm="HS256"), expiresIn

def validateToken(token, rol):
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    decodedExpiresIn = decoded["expiresIn"]
    decodedRol = decoded["rol"]

    if decodedExpiresIn < int(time.time()):
        return "Token Expired"
    if rol != "all":
        if decodedRol != rol:
            return "You dont have permission to access this site"

    return None

def getUserFromToken(token):
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    username = decoded["username"]

    return User.objects.get(username=username)


