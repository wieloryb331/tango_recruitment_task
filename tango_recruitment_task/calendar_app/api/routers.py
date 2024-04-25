from rest_framework import routers

from calendar_app.api.viewsets import EventViewSet, LocationViewSet

router = routers.SimpleRouter()

router.register(r'locations', LocationViewSet, basename="locations")
router.register(r'events', EventViewSet, basename="events")