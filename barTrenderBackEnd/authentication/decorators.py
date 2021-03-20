from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from authentication.utils import validateToken
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

APIKEY = "apikeytest"

def apikey_required(view_func):
    def wrapped(self, request, **kwargs):
        try:
            apiKey = request.headers["apiKey"]
        except:
            return Response({"error": "No API KEY Provided"}, HTTP_401_UNAUTHORIZED)
            
        if apiKey != APIKEY:
            return Response({"error": "A400"}, HTTP_401_UNAUTHORIZED)
        return view_func(self, request, **kwargs)

    return wrapped

def token_required(rol):
    def wrapper(view_func):
        def wrapped(self, request, **kwargs):
            
            try:
                token = request.headers["token"]
            except:
                return Response({"error": "No token Provided"}, HTTP_401_UNAUTHORIZED)

            error = validateToken(token,rol)
            if error :
                return Response({"error": error}, HTTP_401_UNAUTHORIZED)

            return view_func(self, request, **kwargs)

        return wrapped
    return wrapper