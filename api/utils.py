# File: api/utils.py

import math
import requests
import logging
import xml.etree.ElementTree as ET
from django.core.mail import send_mail
from django.conf import settings
from .models import Specialist

# Set up basic logging
logger = logging.getLogger(__name__)

# --- Distance Calculation ---

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the earth (specified in decimal degrees) using the
    Equirectangular approximation.

    Args:
        lat1 (float): Latitude of point 1
        lon1 (float): Longitude of point 1
        lat2 (float): Latitude of point 2
        lon2 (float): Longitude of point 2

    Returns:
        float: Distance in kilometers, or None if input is invalid.
    """
    # Check for valid inputs (simple check)
    if None in [lat1, lon1, lat2, lon2]:
        logger.warning("Invalid input coordinates for distance calculation.")
        return None

    try:
        R = 6371  # Earth radius in kilometers
        
        # Convert latitude and longitude to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine formula
        a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon/2) * math.sin(delta_lon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c

        return distance
    except Exception as e:
        logger.error(f"Error calculating distance: {e}", exc_info=True)
        return None

# --- Address Lookup Service Interaction ---

# Base URL for the Address Lookup Service (Check DATA.GOV.HK for the correct API endpoint)
ADDRESS_LOOKUP_API_URL = "https://www.als.ogcio.gov.hk/lookup"

def get_location_details(building_name):
    """
    Fetches latitude, longitude, and GeoAddress for a given building name
    using the DATA.GOV.HK Address Lookup Service.

    Args:
        building_name (str): The name of the building to look up.

    Returns:
        dict: A dictionary {'latitude': float, 'longitude': float, 'geo_address': str}
              or None if the lookup fails or address is not found.
    """
    if not building_name:
        logger.warning("Building name is required for address lookup.")
        return None

    params = {
        'q': building_name,
        'n': 1  # Request only the first result as per project requirements
    }
    
    headers = {
        'Accept': 'application/xml',  # Explicitly request XML
        'Accept-Language': 'en'
    }

    try:
        response = requests.get(ADDRESS_LOOKUP_API_URL, params=params, headers=headers, timeout=10)

        # --- Add these lines for debugging ---
        print(f"--- Debug API Response ---")
        print(f"URL Requested: {response.url}") # See the exact URL requested
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text:\n{response.text[:500]}...") # Print first 500 chars of response text
        print(f"--- End Debug ---")
        # --- End of added lines ---

        response.raise_for_status() # Check for 4xx/5xx errors

        # Parse XML response
        root = ET.fromstring(response.text)
        
        # Navigate XML structure - adjust paths based on the actual XML structure
        suggested = root.find('.//SuggestedAddress/Address/PremisesAddress')
        if suggested is not None:
            # Get geographic coordinates
            geo_info = suggested.find('.//GeospatialInformation')
            if geo_info is not None:
                latitude = float(geo_info.find('Latitude').text)
                longitude = float(geo_info.find('Longitude').text)
                
                # Get GeoAddress
                geo_address = suggested.find('GeoAddress')
                geo_address_text = geo_address.text if geo_address is not None else None

                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'geo_address': geo_address_text
                }
            
        logger.warning(f"No valid location data found for '{building_name}'")
        return None

    except ET.ParseError as e:
        logger.error(f"Failed to parse XML response for '{building_name}': {e}", exc_info=True)
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed for '{building_name}': {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during address lookup for '{building_name}': {e}", exc_info=True)
        return None
    
def send_reservation_notification(reservation, action='create'):
    """
    Send email notification to all specialists about reservation changes.
    
    Args:
        reservation: The Reservation instance
        action: String indicating the type of action ('create', 'update', or 'delete')
    """
    university_codes = reservation.accommodation.universities.values_list('code', flat=True)
    specialists = Specialist.objects.filter(campus__university__in=university_codes)

    # Define email content based on action
    if action == 'create':
        subject = f'UniHaven: New Reservation #{reservation.id}'
        message = f"""
New reservation details:

Accommodation: {reservation.accommodation}
Student: {reservation.student.name} ({reservation.student.email})
Period: {reservation.reservation_start} to {reservation.reservation_end}
Status: {reservation.status}

Please review this reservation in the system.
"""
    elif action == 'update':
        subject = f'UniHaven: Reservation #{reservation.id} Updated'
        message = f"""
Reservation has been updated:

Accommodation: {reservation.accommodation}
Student: {reservation.student.name} ({reservation.student.email})
Period: {reservation.reservation_start} to {reservation.reservation_end}
New Status: {reservation.status}

Please review these changes in the system.
"""
    elif action == 'delete':
        subject = f'UniHaven: Reservation #{reservation.id} Cancelled'
        message = f"""
Reservation has been cancelled:

Accommodation: {reservation.accommodation}
Student: {reservation.student.name} ({reservation.student.email})
Previously Reserved Period: {reservation.reservation_start} to {reservation.reservation_end}

The accommodation is now available for new reservations.
"""

    specialist_emails = list(specialists.values_list('email', flat=True))

    if specialist_emails:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=specialist_emails,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            return False
    return False