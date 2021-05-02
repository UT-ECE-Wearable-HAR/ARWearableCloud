from django.urls import path, include
from .views import *
from .inference import Inference


urlpatterns = [
    path('login/', Login),
    path('logout/', Logout),
    path('register/', Register),
    path('connect/', Connect),
    path('inference/', Inference),
    path('getimgs/', GetImgs),
    path('gettimestamps/', GetTimestamps)
]
