from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase # Use APITestCase for DRF features
from .models import Campus, Accommodation
# Import other models as needed

class CampusAPITests(APITestCase):
    def test_create_campus(self):
        """
        Ensure we can create a new campus object.
        """
        url = reverse('campus-list-create') # Uses the 'name' from urls.py
        data = {'name': 'HKU Main Campus Test', 'latitude': 22.28405, 'longitude': 114.13784}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campus.objects.count(), 1)
        self.assertEqual(Campus.objects.get().name, 'HKU Main Campus Test')

    def test_list_campuses(self):
        """
        Ensure we can list campus objects.
        """
        # Create a campus first
        Campus.objects.create(name='HKU Main Campus Test', latitude=22.28405, longitude=114.13784)
        url = reverse('campus-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Check if one campus is returned

    # Add tests for GET detail, PUT, DELETE for Campus...

class AccommodationAPITests(APITestCase):
    def test_create_accommodation(self):
        """
        Ensure we can create a new accommodation object.
        (Still needs dummy lat/lon for now)
        """
        url = reverse('accommodation-list-create')
        data = {
            "availability_start": "2025-07-01", "availability_end": "2025-11-30",
            "type": "Flat", "beds": 3, "bedrooms": 2, "price": "5000.00",
            "building_name": "Test Building Gamma", "latitude": 22.3, "longitude": 114.3, # Dummy not from the gov data
            "address": "456 Test Avenue", "flat_number": "Unit 1", "floor_number": "5",
            "owner_name": "Ms. Landlord", "owner_contact": "12345678"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Accommodation.objects.count(), 1)
        self.assertEqual(Accommodation.objects.get().building_name, 'Test Building Gamma')

    # Add tests for GET list, GET detail, PUT, DELETE for Accommodation...