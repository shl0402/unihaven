from django.core.management.base import BaseCommand
from api.models import Campus, Student, Accommodation

class Command(BaseCommand):
    help = 'Sets up test data for API testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')

        # Clear existing test data
        Student.objects.all().delete()
        Campus.objects.all().delete()
        Accommodation.objects.all().delete()
        
        # Create test campus
        campus, created = Campus.objects.get_or_create(
            name='Test Campus',
            defaults={
                'latitude': 22.28405,
                'longitude': 114.13784
            }
        )
        self.stdout.write(f'{"Created" if created else "Retrieved"} test campus with ID: {campus.id}')

        # Create test student with unique email
        student, created = Student.objects.get_or_create(
            email='test@example.com',
            defaults={
                'name': 'Test Student',
                'password': 'testpass123',
                'campus': campus,
                'contact': '12345678'
            }
        )
        self.stdout.write(f'{"Created" if created else "Retrieved"} test student with ID: {student.id}')

        # Create test accommodation
        accommodation, created = Accommodation.objects.get_or_create(
            building_name='Test Building',
            floor_number='1',
            flat_number='A',
            defaults={
                'availability_start': '2025-05-01',
                'availability_end': '2025-12-31',
                'type': 'Room',
                'beds': 1,
                'bedrooms': 1,
                'price': '1500.00',
                'latitude': 22.2,
                'longitude': 114.2,
                'address': '123 Test Street',
                'owner_name': 'Test Owner',
                'owner_contact': '87654321'
            }
        )
        self.stdout.write(f'{"Created" if created else "Retrieved"} test accommodation with ID: {accommodation.id}')

        self.stdout.write(self.style.SUCCESS('Test data setup complete!'))
        self.stdout.write('\nTest IDs to use:')
        self.stdout.write(f'Campus ID: {campus.id}')
        self.stdout.write(f'Student ID: {student.id}')
        self.stdout.write(f'Accommodation ID: {accommodation.id}')