from datetime import timedelta
import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from calendar_app.models import Event, Location

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email")

class LocationRetrieveSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)

    class Meta:
        model = Location
        fields = ("id", "manager", "name", "address")

class LocationCreateSerializer(serializers.ModelSerializer):
    manager_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Location
        fields = ("id", "manager_id", "name", "address")

class TimezoneAwareToRepresentationSerializerMixin:
    """
    Mixin responsible for returning date_start and date_end as timezone aware
    """
    def to_representation(self, instance):
        tz = self.context["request"].user.tz
        self.fields['date_start'] = serializers.DateTimeField(default_timezone=tz)
        self.fields['date_end'] = serializers.DateTimeField(default_timezone=tz)
        return super().to_representation(instance)

class EventRetrieveSerializer(TimezoneAwareToRepresentationSerializerMixin, serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    location = LocationRetrieveSerializer()
    
    class Meta:
        model = Event
        fields = ("id", "owner", "name", "agenda", "date_start", "date_end", "participants", "location")


class EventCreateSerializer(TimezoneAwareToRepresentationSerializerMixin, serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    participants = serializers.ListField(child=serializers.EmailField(), write_only=True)
    location_id = serializers.IntegerField(min_value=1, required=False)
    
    class Meta:
        model = Event
        fields = ("id", "owner", "name", "agenda", "date_start", "date_end", "participants", "location_id")
    
    def to_internal_value(self, data):
        """
        Make date_start and date_end timezone aware. 
        """
        tz = self.context["request"].user.tz

        date_start = datetime.datetime.strptime(data["date_start"], "%Y-%m-%d %H:%M:%S")
        date_end = datetime.datetime.strptime(data["date_end"], "%Y-%m-%d %H:%M:%S")

        date_start = timezone.make_aware(date_start, tz)
        date_end = timezone.make_aware(date_end, tz)

        data["date_start"] = date_start
        data["date_end"] = date_end
        
        return super().to_internal_value(data)
    
    def validate(self, data):
        if data['date_start'] > data['date_end']:
            raise serializers.ValidationError("End must occur after start")
        if data['date_start'] + timedelta(hours=8) <= data['date_end']:
            raise serializers.ValidationError("Event must not be longer than 8 hours")
        return data

    def validate_location_id(self, value):
        if value is not None:
            user = self.context["request"].user
            # check if the location is located in the same company as user creating the event
            if not Location.objects.filter(manager__company=user.company).exists():
                raise serializers.ValidationError("Location not available")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        user_model = get_user_model()
        participants = user_model.objects.filter(email__in=validated_data.pop("participants"))
        event = Event.objects.create(**validated_data)

        # add participants to event (all at once)
        event_participants_to_create = []
        for participant in participants:
            event_participants_to_create.append(
                event.participants.through(
                    event=event, user=participant
                )
            )
        event.participants.through.objects.bulk_create(event_participants_to_create)

        return event
    

    """
{
    "name": "Daily 1",
    "agenda": "daily super sprawa",
    "date_start": "2024-04-26T11:06:07+02:00",
    "date_end": "2024-04-26T13:06:07+02:00",
    "participants": ["dominik@gmail.com", "dominik2@gmail.com"],
    "location_id": 1
}
{
    "name": "spotkanie dominika2",
    "agenda": "ryby super important",
    "date_start": "2024-04-26 11:06:07",
    "date_end": "2024-04-26 12:06:07",
    "participants": ["dominik@gmail.com", "dominik2@gmail.com"],
    "location_id": 1
}
    """
