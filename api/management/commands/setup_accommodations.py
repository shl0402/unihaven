from django.core.management.base import BaseCommand
from api.models import Accommodation, Campus, AccommodationDistance, University
from datetime import date
from api.utils import calculate_distance

class Command(BaseCommand):
    help = 'Creates test accommodations with real building names'

    def handle(self, *args, **options):
        self.stdout.write('Creating test accommodations...')
        
        # First ensure universities exist
        for uni_code, uni_name in [
            ('HKU', 'The University of Hong Kong'),
            ('CUHK', 'The Chinese University of Hong Kong'),
            ('HKUST', 'Hong Kong University of Science and Technology')
        ]:
            University.objects.get_or_create(code=uni_code, defaults={'name': uni_name})
        
        accommodations = [
            # HKU Accommodations (Generally cheaper, closer to HKU)
            {
                'building_name': 'Hoi Tsing Court',
                'type': 'Flat',
                'beds': 3,
                'bedrooms': 2,
                'price': 15000.00,
                'floor_number': '18',
                'flat_number': 'A',
                'room_number': None,
                'owner_name': 'James Wong',
                'owner_contact': '91234567',
                'availability_start': date(2025, 9, 1),
                'availability_end': date(2026, 8, 31),
                'address': '1 Hoi Ting Road, Tai Kok Tsui',
                'university_codes': ['HKU'],
                'latitude': 22.3185,
                'longitude': 114.1621
            },
            {
                'building_name': 'Kwun Hoi Court',
                'type': 'Room',
                'beds': 1,
                'bedrooms': 1,
                'price': 6500.00,
                'floor_number': '12',
                'flat_number': 'B',
                'room_number': '1',
                'owner_name': 'Mary Chan',
                'owner_contact': '91234568',
                'availability_start': date(2025, 7, 1),
                'availability_end': date(2026, 6, 30),
                'address': '38 Lei King Road, Sai Wan Ho',
                'university_codes': ['HKU'],
                'latitude': 22.2862,
                'longitude': 114.2229
            },
            # CUHK Accommodations (Mid-range prices, closer to CUHK)
            {
                'building_name': 'Kong Shing Court',
                'type': 'Mini hall',
                'beds': 4,
                'bedrooms': 2,
                'price': 18000.00,
                'floor_number': '25',
                'flat_number': 'C',
                'room_number': None,
                'owner_name': 'Peter Lau',
                'owner_contact': '91234569',
                'availability_start': date(2025, 8, 1),
                'availability_end': date(2026, 7, 31),
                'address': '8 Kong Pui Street, Sha Tin',
                'university_codes': ['CUHK'],
                'latitude': 22.4013,
                'longitude': 114.2097
            },
            {
                'building_name': 'Albert House',
                'type': 'Room',
                'beds': 2,
                'bedrooms': 1,
                'price': 8000.00,
                'floor_number': '15',
                'flat_number': 'D',
                'room_number': '2',
                'owner_name': 'Sarah Lee',
                'owner_contact': '91234570',
                'availability_start': date(2025, 9, 1),
                'availability_end': date(2026, 8, 31),
                'address': '20-24 Chik Fuk Street, Tai Wai',
                'university_codes': ['CUHK'],
                'latitude': 22.3731,
                'longitude': 114.1854
            },
            # HKUST Accommodations (Higher-end prices, closer to HKUST)
            {
                'building_name': 'Aldrich Garden',
                'type': 'Flat',
                'beds': 3,
                'bedrooms': 2,
                'price': 22000.00,
                'floor_number': '28',
                'flat_number': 'E',
                'room_number': None,
                'owner_name': 'David Chen',
                'owner_contact': '91234571',
                'availability_start': date(2025, 9, 1),
                'availability_end': date(2026, 8, 31),
                'address': '2 Aldrich Street, Quarry Bay',
                'university_codes': ['HKUST'],
                'latitude': 22.2873,
                'longitude': 114.2105
            },
            {
                'building_name': 'Alfred House',
                'type': 'Room',
                'beds': 1,
                'bedrooms': 1,
                'price': 7500.00,
                'floor_number': '10',
                'flat_number': 'F',
                'room_number': '3',
                'owner_name': 'Emily Wong',
                'owner_contact': '91234572',
                'availability_start': date(2025, 7, 1),
                'availability_end': date(2026, 6, 30),
                'address': '12 Alfred Street, Sai Wan Ho',
                'university_codes': ['HKUST'],
                'latitude': 22.2824,
                'longitude': 114.2219
            },
            {
                'building_name': 'Amber Garden',
                'type': 'Mini hall',
                'beds': 6,
                'bedrooms': 3,
                'price': 25000.00,
                'floor_number': '32',
                'flat_number': 'G',
                'room_number': None,
                'owner_name': 'Michael Zhang',
                'owner_contact': '91234573',
                'availability_start': date(2025, 8, 1),
                'availability_end': date(2026, 7, 31),
                'address': '88 Amber Street, North Point',
                'university_codes': ['HKUST'],
                'latitude': 22.2910,
                'longitude': 114.2020
            },
            {
                'building_name': 'Amber Commercial Building',
                'type': 'Flat',
                'beds': 2,
                'bedrooms': 1,
                'price': 12000.00,
                'floor_number': '20',
                'flat_number': 'H',
                'room_number': None,
                'owner_name': 'Grace Liu',
                'owner_contact': '91234574',
                'availability_start': date(2025, 9, 1),
                'availability_end': date(2026, 8, 31),
                'address': '225 Gloucester Road, Wan Chai',
                'university_codes': ['HKUST'],
                'latitude': 22.2799,
                'longitude': 114.1786
            },
            {
                'building_name': 'Central Plaza Apartments',
                'type': 'Flat',
                'beds': 2,
                'bedrooms': 1,
                'price': 18000.00,
                'floor_number': '15',
                'flat_number': 'D',
                'room_number': None,
                'owner_name': 'John Doe',
                'owner_contact': '91234575',
                'availability_start': date(2025, 9, 1),
                'availability_end': date(2026, 8, 31),
                'address': '18 Harbour Road, Wan Chai',
                'university_codes': ['HKU', 'CUHK'],
                'latitude': 22.2800,
                'longitude': 114.1733
            },
        ]
        
        for accommodation_data in accommodations:
            university_codes = accommodation_data.pop('university_codes', [])
            
            # Create the accommodation first without universities
            accommodation, created = Accommodation.objects.update_or_create(
                building_name=accommodation_data['building_name'],
                floor_number=accommodation_data['floor_number'],
                flat_number=accommodation_data['flat_number'],
                room_number=accommodation_data['room_number'],
                defaults={
                    'type': accommodation_data['type'],
                    'beds': accommodation_data['beds'],
                    'bedrooms': accommodation_data['bedrooms'],
                    'price': accommodation_data['price'],
                    'owner_name': accommodation_data['owner_name'],
                    'owner_contact': accommodation_data['owner_contact'],
                    'availability_start': accommodation_data['availability_start'],
                    'availability_end': accommodation_data['availability_end'],
                    'address': accommodation_data['address'],
                    'latitude': accommodation_data['latitude'],
                    'longitude': accommodation_data['longitude']
                }
            )
            
            # Now add the universities
            for code in university_codes:
                university = University.objects.get(code=code)
                accommodation.universities.add(university)

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created accommodation: {accommodation.building_name} ({accommodation.type})'
                ))
            else:
                self.stdout.write(
                    f'Updated existing accommodation: {accommodation.building_name}'
                )

        self.stdout.write(self.style.SUCCESS('Test accommodations setup completed!'))

        # After all accommodations are created:
        campuses = list(Campus.objects.all())
        for accommodation in Accommodation.objects.all():
            for campus in campuses:
                distance = calculate_distance(
                    accommodation.latitude, accommodation.longitude,
                    campus.latitude, campus.longitude
                )
                AccommodationDistance.objects.update_or_create(
                    accommodation=accommodation,
                    campus=campus,
                    defaults={'distance': distance or float('inf')}
                )

        self.stdout.write(self.style.SUCCESS('Accommodation distances setup completed!'))