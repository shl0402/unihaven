import requests # Make sure 'requests' is installed
from django.core.management.base import BaseCommand

# Base URL of your running dev server
BASE_URL = "http://127.0.0.1:8000/api"

class Command(BaseCommand):
    help = 'Runs basic tests against the UniHaven API endpoints (requires dev server running)'

    def handle(self, *args, **options):
        self.stdout.write("Starting basic API tests...")

        try:
            # --- Test Campus ---
            self.stdout.write("\n--- Testing Campuses ---")
            # POST (Create)
            campus_data = {'name': 'Test Campus Alpha', 'latitude': 22.0, 'longitude': 114.0}
            response = requests.post(f"{BASE_URL}/campuses/", json=campus_data)
            self.stdout.write(f"POST /campuses/ - Status: {response.status_code}")
            if response.status_code == 201:
                campus_id = response.json().get('id')
                self.stdout.write(f"  Created Campus ID: {campus_id}")

                # GET List
                response = requests.get(f"{BASE_URL}/campuses/")
                self.stdout.write(f"GET /campuses/ - Status: {response.status_code}, Count: {len(response.json())}")

                # GET Detail
                response = requests.get(f"{BASE_URL}/campuses/{campus_id}/")
                self.stdout.write(f"GET /campuses/{campus_id}/ - Status: {response.status_code}, Name: {response.json().get('name')}")

                # PUT (Update)
                updated_data = {'name': 'Test Campus Alpha Updated', 'latitude': 22.1, 'longitude': 114.1}
                response = requests.put(f"{BASE_URL}/campuses/{campus_id}/", json=updated_data)
                self.stdout.write(f"PUT /campuses/{campus_id}/ - Status: {response.status_code}")

                # DELETE
                response = requests.delete(f"{BASE_URL}/campuses/{campus_id}/")
                self.stdout.write(f"DELETE /campuses/{campus_id}/ - Status: {response.status_code}") # Should be 204

            else:
                self.stderr.write(f"  Failed to create campus: {response.text}")


            # --- Test Accommodation ---
            self.stdout.write("\n--- Testing Accommodations ---")
            # POST (Create) - Needs dummy lat/lon for now
            # Assumes a Campus with ID=1 exists, or uses the one created above if possible
            # You might need to create a campus first or ensure one exists
            # Use actual required fields from your model/serializer
            accom_data = {
                "availability_start": "2025-06-01",
                "availability_end": "2025-12-31",
                "type": "Room", # Must be one of the choices in models.py
                "beds": 1,
                "bedrooms": 1,
                "price": "1500.00",
                "building_name": "Test Building Beta",
                "latitude": 22.2, # Dummy - Step 7 will handle this
                "longitude": 114.2, # Dummy - Step 7 will handle this
                "address": "123 Test Street",
                "flat_number": "B",
                "floor_number": "10",
                "owner_name": "Mr. Owner",
                "owner_contact": "98765432"
                # room_number is optional (nullable/blank)
                # geo_address is optional (nullable/blank)
                # is_reserved, average_rating, rating_count have defaults
            }
            response = requests.post(f"{BASE_URL}/accommodations/", json=accom_data)
            self.stdout.write(f"POST /accommodations/ - Status: {response.status_code}")
            if response.status_code == 201:
                 accom_id = response.json().get('id')
                 self.stdout.write(f"  Created Accommodation ID: {accom_id}")
                 # Add GET list, GET detail, PUT, DELETE tests similar to Campus
            else:
                 self.stderr.write(f"  Failed to create accommodation: {response.text}")

        except requests.exceptions.ConnectionError:
            self.stderr.write(self.style.ERROR("Connection Error: Make sure the Django development server is running."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

        self.stdout.write("\nBasic API tests finished.")