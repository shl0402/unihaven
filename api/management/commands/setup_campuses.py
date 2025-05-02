from django.core.management.base import BaseCommand
from api.models import Campus

class Command(BaseCommand):
    help = 'Creates initial campus data for universities'

    def handle(self, *args, **options):
        self.stdout.write('Creating campus data...')

        # Define campus data
        campuses = [
            # Main University Campuses
            {
                'name': 'HKU',
                'latitude': 22.28405,
                'longitude': 114.13784,
                'university': 'HKU'
            },
            {
                'name': 'CUHK',
                'latitude': 22.41907,
                'longitude': 114.20693,
                'university': 'CUHK'
            },
            {
                'name': 'HKUST',
                'latitude': 22.33584,
                'longitude': 114.26355,
                'university': 'HKUST'
            },
            # HKU Specific Campuses
            {
                'name': 'HKU Main Campus',
                'latitude': 22.28405,
                'longitude': 114.13784,
                'university': 'HKU'
            },
            {
                'name': 'Sassoon Road Campus',
                'latitude': 22.2675,
                'longitude': 114.12881,
                'university': 'HKU'
            },
            {
                'name': 'Swire Institute of Marine Science',
                'latitude': 22.20805,
                'longitude': 114.26021,
                'university': 'HKU'
            },
            {
                'name': 'Kadoorie Centre',
                'latitude': 22.43022,
                'longitude': 114.11429,
                'university': 'HKU'
            },
            {
                'name': 'Faculty of Dentistry',
                'latitude': 22.28649,
                'longitude': 114.14426,
                'university': 'HKU'
            },
            # HKUST Specific Campus
            {
                'name': 'The Chinese University of Hong Kong Campus',
                'latitude': 22.41907,
                'longitude': 114.20693,
                'university': 'CUHK'
            },
            # CUHK Specific Campus
            {
                'name': 'Hong Kong University of Science and Technology Campus',
                'latitude': 22.33584,
                'longitude': 114.26355,
                'university': 'HKUST'
            },
        ]

        # Create or update campuses
        for campus_data in campuses:
            campus, created = Campus.objects.update_or_create(
                name=campus_data['name'],
                university=campus_data['university'],
                defaults={
                    'latitude': campus_data['latitude'],
                    'longitude': campus_data['longitude']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created campus: {campus.name} ({campus.university})'
                ))
            else:
                self.stdout.write(
                    f'Updated existing campus: {campus.name} ({campus.university})'
                )

        self.stdout.write(self.style.SUCCESS('Campus setup completed!'))