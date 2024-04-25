from django.db import models
from django.contrib.auth.models import AbstractUser

from timezone_field import TimeZoneField

from calendar_app.models import Company

# Create your models here.

class User(AbstractUser):
    company = models.ForeignKey(Company, related_name="users", on_delete=models.CASCADE, null=True, blank=True)
    tz = TimeZoneField(default="Europe/Warsaw")
    