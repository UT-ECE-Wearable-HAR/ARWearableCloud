from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)


class ImgCapture(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	img = models.BinaryField()

class MpuCapture(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	mpu_data = models.BinaryField()
