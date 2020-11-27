from django.shortcuts import render,HttpResponse
from django.contrib.auth import logout,login,authenticate
from UserProfile.models import UserProfile 
from django.core import serializers
from django.contrib.auth.models import User
from _thread import *
from .socketthread import *
import threading 
import logging

# Create your views here.


def Login(request):
    logger = logging.getLogger("mainlogger")    
    if request.method == 'POST':
        user=authenticate(request,username=request.POST.get('username'),password=request.POST.get('password'))
        if user is not None:
            login(request,user)
            logger.info("starting thread")
            start_new_thread(socketthread, (user,))
            return HttpResponse("Logged in")
        else:
            return HttpResponse("Error Logging In")

def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse("Logged Out")
    else:
        return HttpResponse("Error Logging Out")

def Register(request):
    if request.method == 'POST':
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        user.save()
        profile = UserProfile(user = user)
        profile.save()
        return HttpResponse("Registered!")
    else:
        return HttpResponse("Error Registering")