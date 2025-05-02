from django.core.management.base import BaseCommand
from api.models import Campus, Student, Specialist

class Command(BaseCommand):
    help = 'Creates initial students and specialists for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating test students and specialists...')

        # First, get all campuses by university
        hku_campuses = Campus.objects.filter(university='HKU')
        cuhk_campuses = Campus.objects.filter(university='CUHK')
        hkust_campuses = Campus.objects.filter(university='HKUST')

        # Define test students data
        students = [
            # HKU Students
            {
                'name': 'John Smith',
                'email': 'john.smith@connect.hku.hk',
                'contact': '98765432',
                'campus': hku_campuses.first()
            },
            {
                'name': 'Mary Wong',
                'email': 'mary.wong@connect.hku.hk',
                'contact': '98765433',
                'campus': hku_campuses.first()
            },
            # CUHK Students
            {
                'name': 'Peter Chan',
                'email': 'peter.chan@link.cuhk.edu.hk',
                'contact': '98765434',
                'campus': cuhk_campuses.first()
            },
            {
                'name': 'Lisa Lee',
                'email': 'lisa.lee@link.cuhk.edu.hk',
                'contact': '98765435',
                'campus': cuhk_campuses.first()
            },
            # HKUST Students
            {
                'name': 'David Lam',
                'email': 'david.lam@connect.ust.hk',
                'contact': '98765436',
                'campus': hkust_campuses.first()
            },
            {
                'name': 'Sarah Chen',
                'email': 'sarah.chen@connect.ust.hk',
                'contact': '98765437',
                'campus': hkust_campuses.first()
            },
        ]

        # Define test specialists data
        specialists = [
            # HKU Specialists
            {
                'name': 'Samuel Hui',
                'email': 'samuelhui040402@gmail.com',
                'contact': '91234567',
                'campus': hku_campuses.first()
            },
            {
                'name': 'Samuel Hui (HKU)',
                'email': 'shl0402@connect.hku.hk',
                'contact': '91234568',
                'campus': hku_campuses.first()
            },
            {
                'name': 'Jane Wilson',
                'email': 'jane.wilson@hku.hk',
                'contact': '91234569',
                'campus': hku_campuses.first()
            },
            # CUHK Specialists
            {
                'name': 'Michael Zhang',
                'email': 'michael.zhang@cuhk.edu.hk',
                'contact': '91234570',
                'campus': cuhk_campuses.first()
            },
            {
                'name': 'Emily Wang',
                'email': 'emily.wang@cuhk.edu.hk',
                'contact': '91234571',
                'campus': cuhk_campuses.first()
            },
            # HKUST Specialists
            {
                'name': 'Robert Kim',
                'email': 'robert.kim@ust.hk',
                'contact': '91234572',
                'campus': hkust_campuses.first()
            },
            {
                'name': 'Grace Liu',
                'email': 'grace.liu@ust.hk',
                'contact': '91234573',
                'campus': hkust_campuses.first()
            },
        ]

        # Create students
        for student_data in students:
            student, created = Student.objects.update_or_create(
                email=student_data['email'],
                defaults={
                    'name': student_data['name'],
                    'contact': student_data['contact'],
                    'campus': student_data['campus']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created student: {student.name} ({student.email})'
                ))
            else:
                self.stdout.write(
                    f'Updated existing student: {student.name} ({student.email})'
                )

        # Create specialists
        for specialist_data in specialists:
            specialist, created = Specialist.objects.update_or_create(
                email=specialist_data['email'],
                defaults={
                    'name': specialist_data['name'],
                    'contact': specialist_data['contact'],
                    'campus': specialist_data['campus']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created specialist: {specialist.name} ({specialist.email})'
                ))
            else:
                self.stdout.write(
                    f'Updated existing specialist: {specialist.name} ({specialist.email})'
                )

        self.stdout.write(self.style.SUCCESS('Test users setup completed!'))