from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)

class ImgCapture(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	date = models.DateTimeField(blank=True, default=now)
	img = models.BinaryField()

class MpuCapture(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	date = models.DateTimeField(blank=True, default=now)
	mpu_data = models.BinaryField()
