from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.contrib.auth import logout,login,authenticate
from UserProfile.models import UserProfile 
from django.core import serializers
from django.contrib.auth.models import User
from _thread import *
from .socketthread import *
import threading 
import logging
import json

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

def GetImgs(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        img_ids = body['imgIds']
        ret_json  = {}
        ret_json['imgs'] = []
        for img_id in img_ids:
            try:
                db_entry = DataCapture.objects.get(id=img_id)
                ret_json['imgs'].append(str(getattr(db_entry, "img")))
            except DataCapture.DoesNotExist:
                ret_json['imgs'].append("0")
        return JsonResponse(ret_json)

def GetTimestamps(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        frame_ids = body['frameIds']
        ret_json = {}
        ret_json['timestamps'] = []
        for frame in frame_ids:
            try:
                db_entry_start = DataCapture.objects.get(id=frame["start"])
                db_entry_end = DataCapture.objects.get(id=frame["end"])
                ts_summary = {}
                ts_summary['start'] = getattr(db_entry_start, "date")
                ts_summary['end'] = getattr(db_entry_end, "date")
                ret_json['timestamps'].append(ts_summary)
            except DataCapture.DoesNotExist:
                ret_json['timestamps'].append({'start': -1, 'end': -1})
        return JsonResponse(ret_json)