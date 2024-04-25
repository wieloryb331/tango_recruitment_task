from datetime import timedelta
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from calendar_app.models import Event, Company, Location
from users.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class EventTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create()
        self.user = User.objects.create(
            username="dominik_szymkowiak",
            email="dominik@gmail.com",
            company=self.company
        )
        self.location = Location.objects.create(
            manager=self.user,
            name="conference room",
            address="ul. Wielkopolska 1 Poznan 61-321 Poland"
        )
    
    def test_event_can_be_created_without_location(self):
        data = {
            "owner": self.user,
            "name": "event name",
            "agenda": "event agenda",
            "date_start": timezone.now(),
            "date_end": timezone.now() + timedelta(hours=1),
        }
        event = Event.objects.create(**data)
        self.assertIsNotNone(event)
    
    def test_event_can_be_created_with_location(self):
        data = {
            "owner": self.user,
            "name": "event name",
            "agenda": "event agenda",
            "date_start": timezone.now(),
            "date_end": timezone.now() + timedelta(hours=1),
            "location": self.location
        }
        event = Event.objects.create(**data)
        self.assertIsNotNone(event)
    
    def test_event_with_date_start_gt_date_end_fails(self):
        data = {
            "owner": self.user,
            "name": "event name",
            "agenda": "event agenda",
            "date_start": timezone.now(),
            "date_end": timezone.now() - timedelta(hours=1),
            "location": self.location
        }
        with self.assertRaises(IntegrityError):
            event = Event.objects.create(**data)
    
    def test_event_with_duration_gt_8_hours_fails(self):
        data = {
            "owner": self.user,
            "name": "event name",
            "agenda": "event agenda",
            "date_start": timezone.now(),
            "date_end": timezone.now() + timedelta(hours=8, minutes=1),
            "location": self.location
        }
        with self.assertRaises(IntegrityError):
            event = Event.objects.create(**data)

    def test_event_without_owner_fails(self):
        data = {
            "owner": None,
            "name": "event name",
            "agenda": "event agenda",
            "date_start": timezone.now(),
            "date_end": timezone.now() + timedelta(hours=8, minutes=1),
            "location": self.location
        }
        with self.assertRaises(IntegrityError):
            event = Event.objects.create(**data)

class EventAPITestCase(APITestCase):
    def setUp(self):
        password = "password"
        self.company = Company.objects.create()
        self.user = User.objects.create(
            username="dominik_szymkowiak",
            email="dominik@gmail.com",
            company=self.company
        )
        self.user.set_password(password)
        self.user.save()
        logged_in = self.client.login(username=self.user.username, password=password)
    
    def tearDown(self):
        self.client.logout()
    
    def test_create_event_without_location(self):
        url = reverse("events-list")
        data = {
            "name": "spotkanie dominika",
            "agenda": "planning poker",
            "date_start": "2024-04-26 11:06:07",
            "date_end": "2024-04-26 12:06:07",
            "participants": ["dominik@gmail.com"],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_event_with_location(self):
        location = Location.objects.create(
            manager=self.user,
            name="conference room",
            address="ul. Wielkopolska 1 Poznan 61-321 Poland"
        )
        url = reverse("events-list")
        data = {
            "name": "spotkanie dominika2",
            "agenda": "planning poker",
            "date_start": "2024-04-26 11:06:07",
            "date_end": "2024-04-26 12:06:07",
            "participants": ["dominik@gmail.com"],
            "location_id": location.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
