from django.contrib.auth.models import User
from authentication.models import Client, Owner
from django.conf import settings
import json, pytz, re, time, jwt
import datetime

HOURS = 24

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
        return "A006"
        
    decodedExpiresIn = decoded["expiresIn"]
    decodedRol = decoded["rol"]

    if decodedExpiresIn < int(time.time()):
        return "A007"
    if rol != "all":
        if decodedRol != rol:
            return "A008"

    return None

def getUserFromToken(token):
    decoded = jwt.decode(token, settings.TOKEN_SECRET, algorithms=["HS256"])
    username = decoded["username"]

    return User.objects.get(username=username)

def getSignupData(request):
    try: res = json.loads(request.body)
    except: return None, "Z001"

    if 'email' not in res or 'password' not in res or 'rol' not in res:
            return None, "Z001"
    
    rol = res["rol"]

    if rol == "client":
        if 'birthday' not in res:
            return None, "Z001"
    elif rol == "owner":
        if 'phone' not in res:
            return None, "Z001"
    else:
        return None, "A011"
    
    return res, None

def validateSignupData(body):
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", body["email"]):
        return "A015"

    if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$", body["password"]):
        return "A016"
    
    if("phone" in body):
        if not re.match(r"^\d{9}$", str(body["phone"])) or type(body["phone"]) != int:
            return "Z003"

    if("birthday" in body):
        try: datetime.datetime.fromtimestamp(body["birthday"], pytz.timezone('Europe/Madrid'))
        except: return "Z002"

    return None

def createUser(body):

    try: user = User.objects.create_user(username=body["email"], password=body["password"])
    except Exception as ex:
        if(ex.args[0] == "UNIQUE constraint failed: auth_user.username"):
            return None, "A013"
        else:
            return None, "A012"

    if body["rol"] == "owner":
        try: Owner.objects.create(user=user, phone=body["phone"])
        except Exception as ex:
            print(ex.args[0])
            if(ex.args[0] == "UNIQUE constraint failed: authentication_owner.phone"):
                return None, "A014"
            else:
                return None, "A012"
    elif body["rol"] == "client":
        try: Client.objects.create(user=user, birthday=datetime.datetime.fromtimestamp(body["birthday"], pytz.timezone('Europe/Madrid')))
        except Exception as ex: 
            print(ex)
            return None, "A012"

    return user, None

