from .models import UserProfile, ImgCapture, MpuCapture
from django.contrib import admin

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ImgCapture)
admin.site.register(MpuCapture)