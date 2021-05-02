from django.contrib.auth.models import User
from authentication.models import Client, Owner
from django.conf import settings
from dateutil.relativedelta import relativedelta
import json, pytz, re, time, jwt
import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from payments.utils import validate_paypal_payment
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

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

    if "password" in body:
        if not re.match(r"(?=.*[-!¡#$@*%º·¬ª'`´¨^=+&(){}.:;<>¿?_])(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}", body["password"]):
            return "A016"
    
    if "phone" in body:
        if not re.match(r"^\d{9}$", str(body["phone"])) or type(body["phone"]) != int:
            return "Z003"

    if "birthday" in body:
        try: datetime.datetime.fromtimestamp(body["birthday"], pytz.timezone('Europe/Madrid'))
        except: return "Z002"

    return None


def validateSignupDataGoogle(body):

    if "phone" in body:
        if not re.match(r"^\d{9}$", str(body["phone"])) or type(body["phone"]) != int:
            return "Z003"

    if "birthday" in body:
        try:
            date1 = datetime.datetime.fromtimestamp(body["birthday"])
            date2 = datetime.datetime.now()
            difference_in_years = relativedelta(date2, date1).years

            if difference_in_years < 18:
                return "Z004"

        except Exception as e:
            return "Z002"


    return None


def createUser(body):

    user = User(username=body["email"])
    user.set_password(body["password"])
    try: user.full_clean()
    except ValidationError as e:
            key = str(list(e.message_dict.keys())[0])
            err_msg = e.message_dict[key][0]
            if "A user with that username already exists" in err_msg:
                return None, "A013"
            else:
                return None, "E00X"
    user.save()

    if body["rol"] == "owner":
        owner = Owner(user=user, phone=body["phone"])
        try: owner.full_clean()
        except ValidationError as e:
            key = str(list(e.message_dict.keys())[0])
            err_msg = e.message_dict[key][0]
            user.delete()
            if "Owner with this Phone already exists" in err_msg:
                return None, "A014"
            else:
                return None, "E00X"

        owner.save()

    elif body["rol"] == "client":
        client = Client(user=user, birthday=datetime.datetime.fromtimestamp(body["birthday"], pytz.timezone('Europe/Madrid')))
        try: client.full_clean()
        except ValidationError as e:
            key = str(list(e.message_dict.keys())[0])
            err_msg = e.message_dict[key][0]
            user.delete()
            print(err_msg)
            if "client with this Phone already exists" in err_msg:
                return None, "A014"
            else:
                return None, "E00X"

        client.save()
    else:
        return None, "E00X"

    return user, None

def setpremium(token, order_id, create_time):

    user = getUserFromToken(token)
    owner = Owner.objects.filter(user=user).get()

    err_code = validate_paypal_payment(order_id, create_time)
    if err_code is not None:
        return err_code

    owner.premium = True
    owner.premium_end_date = datetime.datetime.now(pytz.utc) + relativedelta(months=+1)

    owner.save()

def isPremium(user, rol):
    if rol == 'client':
        return False
    
    owner = Owner.objects.filter(user=user).get()
    if not owner.premium:
        return False

    if owner.premium_end_date == None:
        return False

    if owner.premium_end_date < datetime.date.today():
        owner.premium = False
        owner.save()
        return False
    
    return True

def valid_user_update(user, data):

    user = authenticate(username=user.username, password=data['old_password'])
    if user is None:
        return "A018"

    try:
        valid = validateSignupData(data)

        if valid != None:
            return valid

    except:
        return "E00X"

    return None

def valid_data_update(data, rol):
    if 'email' not in data or 'old_password' not in data or 'name' not in data or 'surname' not in data:
        return "Z001"

    if rol == "client":
        if "birthday" not in data:
            return "Z001"

    if rol == "owner":
        if "phone" not in data:
            return "Z001"

    return None

def authMethodOfUser(user):
    method = 'google'
    if user.has_usable_password():
        method = 'password'
    return method