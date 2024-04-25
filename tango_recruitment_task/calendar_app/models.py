from datetime import timedelta
import uuid
from django.db import models
from django.db.models import Q, CheckConstraint, F
from django.conf import settings


# Create your models here.

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class Location(models.Model):
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="managed_locations")
    name = models.CharField(max_length=64, blank=False, null=False)
    # address field should look a little different, but for the sake of this task I went with the simplest version
    # if the app was supposed to be used only in Poland I'd try to user TERYT registry
    # if the app was supposed to be used anywhere in the world I'd probably create a separate model
    # with fields such as address1, address2, city, postal_code, country
    # and country would be a field from django_countries package
    address = models.TextField()

class Event(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_events")
    name = models.CharField(max_length=64, blank=False, null=False)
    agenda = models.TextField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name="events")

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(date_end__lte=F("date_start") + timedelta(hours=8)),
                name="duration_lte_8",
                violation_error_message="Event must not be longer than 8 hours"
            ),
            CheckConstraint(
                check=Q(date_end__gt=F("date_start")),
                name="date_end_gt_date_start",
                violation_error_message="Date end should occur later than date start"
            ),
        ]
