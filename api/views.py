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
            try:
                user_exists = UserProfile.objects.get(pk=user)
            except UserProfile.DoesNotExist:
                profile = UserProfile(user = user)
                profile.save()
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
        if User.objects.filter(username=request.POST.get('username')).exists():
            return HttpResponse("Username already in use")
        if User.objects.filter(email=request.POST.get('email')).exists():
            return HttpResponse("Email already in use")
        user = User.objects.create_user(request.POST.get('username'), request.POST.get('email'), request.POST.get('password'))
        user.save()
        profile = UserProfile(user = user)
        profile.save()
        return HttpResponse("Registered")
    else:
        return HttpResponse("Error Registering")

def Connect(request):
    if request.method == 'POST':
        start_new_thread(socketthread, (request.user,))
        return HttpResponse("Connected")
    else:
        return HttpResponse("Error Connecting")