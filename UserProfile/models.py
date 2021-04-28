from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.


class UserProfile(models.Model):
    """User override."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)


class DataCapture(models.Model):
    """Captured data."""

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, default=now)
    sessionid = models.IntegerField()
    img = models.BinaryField()
    quarternion = models.BinaryField()
    gravity = models.BinaryField()
    ypr = models.BinaryField()
    gyro = models.BinaryField()
    accel = models.BinaryField()
    linaccel = models.BinaryField()
    linaccelinworld = models.BinaryField()
    euler = models.BinaryField()
    features = models.BinaryField()


class InferenceCache(models.Model):
    """Cached inferences, stored as JSON."""

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    sessionid = models.IntegerField()
    body = models.TextField()
