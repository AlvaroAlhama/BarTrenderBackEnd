from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from authentication.utils import validateToken
from rest_framework.response import Response
from django.conf import settings
from barTrenderBackEnd.errors import generate_response

def apikey_required(view_func):
    def wrapped(self, request, **kwargs):
        try:
            apiKey = request.headers["apiKey"]
        except:
            return generate_response("A003", 401)
        
        if apiKey != settings.API_KEY:
            return generate_response("A004", 401)
        return view_func(self, request, **kwargs)

    return wrapped

def token_required(rol):
    def wrapper(view_func):
        def wrapped(self, request, **kwargs):
            
            try:
                token = request.headers["token"]
            except:
                return generate_response("A005", 401)

            if token == None:
                return generate_response("A005", 401)

            error = validateToken(token,rol)
            if error:
                return generate_response(error, 401)

            return view_func(self, request, **kwargs)

        return wrapped
    return wrapper