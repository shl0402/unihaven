from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# Based on create_db.py: Campus Table
class Campus(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    university = models.CharField(max_length=50, choices=[
        ('HKU', 'HKU'),
        ('HKUST', 'HKUST'),
        ('CUHK', 'CUHK')
    ])

    def __str__(self):
        return f"{self.name} ({self.university})"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_latitude = self.latitude
        self._original_longitude = self.longitude

# Based on create_db.py: Student Table (Assuming 'Student' maps to a standard User or a custom profile)
class Student(models.Model):
    # student_id implicitly created as 'id'
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    # Storing plain text passwords is very insecure. Django's User model handles this properly.
    # Avoid storing raw passwords in production. This field is included for parity with create_db.py.
    # password = models.CharField(max_length=128)
    contact = models.CharField(max_length=50, blank=True, null=True) # Allow contact to be optional
    # Link to Campus, Protect deletion of Campus if students are linked
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name='students')

    def __str__(self):
        return self.name

# Based on create_db.py: Specialist Table
class Specialist(models.Model):
    # specialist_id implicitly created as 'id'
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    # password = models.CharField(max_length=128)
    contact = models.CharField(max_length=50)
    # Link to Campus, Protect deletion of Campus if specialists are linked
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name='specialists')

    def __str__(self):
        return self.name
    
class University(models.Model):
    code = models.CharField(max_length=10, primary_key=True)  # HKU, CUHK, HKUST
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Universities"

# Based on create_db.py: Accommodation Table
class Accommodation(models.Model):
    # accommodation_id implicitly created as 'id'
    ACCOMMODATION_TYPES = [
        ('Room', 'Room'),
        ('Flat', 'Flat'),
        ('Mini hall', 'Mini hall'),
    ]
    # Removed direct specialist link, will be handled via AccommodationOffering

    # Availability Period
    availability_start = models.DateField()
    availability_end = models.DateField()

    # Details
    type = models.CharField(max_length=20, choices=ACCOMMODATION_TYPES)
    beds = models.IntegerField(validators=[MinValueValidator(1)])
    bedrooms = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]) # Use DecimalField for currency

    # Location Details
    building_name = models.CharField(max_length=255)
    latitude = models.FloatField() # Fetched externally
    longitude = models.FloatField() # Fetched externally
    address = models.TextField() # Full address text
    geo_address = models.CharField(max_length=255, blank=True, null=True) # Unique GeoAddress from external service

    # Detailed Address Components (for uniqueness check)
    room_number = models.CharField(max_length=50, blank=True, null=True) # Nullable as per description
    flat_number = models.CharField(max_length=50)
    floor_number = models.CharField(max_length=50)

    # Owner Details
    owner_name = models.CharField(max_length=255)
    owner_contact = models.CharField(max_length=50)

    # Status fields (consider if these should be derived or stored)
    # The trigger in create_db.py updates is_reserved. Can use signals or override save() in Django.
    # Using a simple field for now.
    is_reserved = models.BooleanField(default=False) # Changed from INTEGER
    # Triggers in create_db.py update rating fields. Can use signals or override save() in Django.
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    rating_count = models.IntegerField(default=0)

    universities = models.ManyToManyField(University, related_name='accommodations')

    class Meta:
        # Ensure address uniqueness
        unique_together = [['room_number', 'flat_number', 'floor_number', 'geo_address']]
        ordering = ['building_name', 'floor_number', 'flat_number', 'room_number'] # Optional: default ordering

    def __str__(self):
        room_str = f" Room {self.room_number}" if self.room_number else ""
        return f"{self.building_name} Floor {self.floor_number} Flat {self.flat_number}{room_str}"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_latitude = self.latitude
        self._original_longitude = self.longitude

# Based on create_db.py: AccommodationOffering Table (Intermediary for Many-to-Many with Specialist)
class AccommodationOffering(models.Model):
    # offering_id implicitly created as 'id'
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='offered_accommodations')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='managed_offerings')

    class Meta:
        # Ensures one offering per accommodation per campus
        unique_together = [['accommodation', 'campus']]
        ordering = ['campus', 'accommodation']

    @property
    def university(self):
        return self.campus

    def __str__(self):
        return f"{self.accommodation} at {self.campus.name}"
    
# Add this new model after your existing models
class AccommodationDistance(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='distances')
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='accommodation_distances')
    distance = models.FloatField(
        help_text="Distance in kilometers between accommodation and campus"
    )

    class Meta:
        unique_together = [['accommodation', 'campus']]
        ordering = ['distance']  # Default ordering by distance

    def __str__(self):
        return f"{self.accommodation} -> {self.campus}: {self.distance:.1f}km"

# Based on create_db.py: Reservation Table
class Reservation(models.Model):
    # reservation_id implicitly created as 'id'
    STATUS_CHOICES = [
        ('pending', 'Pending'),              # Initial state
        ('confirmed', 'Confirmed'),          # Contract signed state from scenario
        ('canceled', 'Canceled'),            # Canceled by member or specialist
        ('contract_not_signed', 'Contract Not Signed'), # State from scenario (Could map to pending/canceled)
        #('completed', 'Completed'),         # Optional: After stay ends (useful for enabling ratings)
    ]
    # Use Django's User model or the simple Student model defined above
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reservations') # Based on create_db.py
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    reservation_start = models.DateField() # Added based on scenario data
    reservation_end = models.DateField() # Added based on scenario data
    created_at = models.DateTimeField(auto_now_add=True) # Track when reservation was made

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Reservation for {self.accommodation} by {self.student.name} ({self.status})"

# Based on create_db.py: Rating Table
class Rating(models.Model):
    # rating_id implicitly created as 'id'
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Recommended way
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ratings') # Based on create_db.py
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)]) # 0-5 scale
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True) # Use DateTimeField, auto-set on creation

    class Meta:
        # Optional: Prevent multiple ratings by the same user for the same accommodation
        # unique_together = [['student', 'accommodation']]
        ordering = ['-date']

    def __str__(self):
        return f"Rating for {self.accommodation} by {self.student.name}: {self.rating}/5"

from django.db import migrations

def populate_university_data(apps, schema_editor):
    University = apps.get_model('api', 'University')
    Accommodation = apps.get_model('api', 'Accommodation')
    
    # Create the three universities
    for code, name in [
        ('HKU', 'The University of Hong Kong'),
        ('CUHK', 'The Chinese University of Hong Kong'),
        ('HKUST', 'Hong Kong University of Science and Technology')
    ]:
        University.objects.create(code=code, name=name)
    
    # For each accommodation, add its university to the many-to-many relationship
    for accommodation in Accommodation.objects.all():
        if hasattr(accommodation, 'university') and accommodation.university:
            uni_code = accommodation.university
            university = University.objects.get(code=uni_code)
            accommodation.universities.add(university)

class Migration(migrations.Migration):
    dependencies = [
        ('api', 'previous_migration'),  # Replace with actual dependency
    ]

    operations = [
        migrations.RunPython(populate_university_data),
    ]