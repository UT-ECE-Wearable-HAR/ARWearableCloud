from django.urls import path,include
from .views import *

urlpatterns = [
    path('login/',Login),
    path('logout/',Logout),
    path('register/',Register)
]