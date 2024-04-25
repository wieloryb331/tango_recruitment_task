import datetime
from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from calendar_app.api.serializers import LocationRetrieveSerializer, LocationCreateSerializer, EventRetrieveSerializer, EventCreateSerializer
from calendar_app.models import Location, Event
from django.utils import timezone
# Create your views here.

class LocationViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_action_map = {
        "list": LocationRetrieveSerializer,
        "retrieve": LocationRetrieveSerializer,
        "create": LocationCreateSerializer
    }
    def get_serializer_class(self):
        return self.serializer_action_map[self.action]

    def get_queryset(self):
        company = self.request.user.company
        locations = Location.objects.filter(manager__company=company)
        return locations

class EventSearchFiter(SearchFilter):
    search_param = "query"  # just to handle the exact search param given in pdf file

class EventFilterSet(filters.FilterSet):
    day = filters.CharFilter(method='filter_by_day', label="Filter by day")
    location_id = filters.NumberFilter(field_name="location__id", lookup_expr="exact")
    
    class Meta:
        model = Event
        fields = ["day"]

    def filter_by_day(self, queryset, name, value):
        tz = self.request.user.tz
        try:
            day = datetime.datetime.strptime(value, "%Y-%m-%d")
            timezone.activate(tz)
        except ValueError:
            return queryset.none()
        return queryset.filter(Q(date_start__day=day.day) | Q(date_end__day=day.day))
        


class EventViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_action_map = {
        "list": EventRetrieveSerializer,
        "retrieve": EventRetrieveSerializer,
        "create": EventCreateSerializer
    }
    filter_backends = [
        DjangoFilterBackend,
        EventSearchFiter
    ]
    filterset_class = EventFilterSet
    search_fields = ["name", "agenda"]

    def get_serializer_class(self):
        return self.serializer_action_map[self.action]

    def get_queryset(self):
        user = self.request.user
        events = Event.objects.filter(Q(participants__in=[user]) | Q(owner=user)).distinct()
        return events