# File: api/serializers.py

from rest_framework import serializers
from .models import Campus, Student, Specialist, Accommodation, AccommodationOffering, Reservation, Rating, AccommodationDistance, University
from drf_spectacular.utils import (
    extend_schema, 
    extend_schema_view,
    OpenApiParameter, 
    OpenApiTypes,
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer
)

class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = '__all__' # Include all fields: id, name, latitude, longitude

class StudentSerializer(serializers.ModelSerializer):
    # Make campus representation more readable (optional, shows ID by default)
    campus_name = serializers.CharField(source='campus.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'contact', 'campus', 'campus_name']
        read_only_fields = ['campus_name'] # Only for reading

class SpecialistSerializer(serializers.ModelSerializer):
    campus_name = serializers.CharField(source='campus.name', read_only=True)

    class Meta:
        model = Specialist
        fields = ['id', 'name', 'email', 'contact', 'campus', 'campus_name']
        read_only_fields = ['campus_name']

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid Accommodation Example',
            value={
                'building_name': 'Ocean Shores Tower 13',
                'type': 'Flat',
                'beds': 2,
                'bedrooms': 1,
                'price': '1500.00',
                'floor_number': '13',
                'flat_number': 'A',
                'room_number': '101',  # Include if not blank
                'owner_name': 'John Doe',
                'owner_contact': '12345678',
                'availability_start': '2025-06-01',
                'availability_end': '2025-12-31',
                'address': '123 Sample Street',
                'universities': ['HKU']  # Added this required field
                # latitude, longitude, geo_address, is_reserved, average_rating, rating_count are read-only
            },
            request_only=True
        ),
        OpenApiExample(
            'Response Example',
            value={
                'id': 1,
                'building_name': 'Ocean Shores Tower 13',
                'type': 'Flat',
                'beds': 2,
                'bedrooms': 1,
                'price': '1500.00',
                'floor_number': '13',
                'flat_number': 'A',
                'room_number': '101',
                'owner_name': 'John Doe',
                'owner_contact': '12345678',
                'availability_start': '2025-06-01',
                'availability_end': '2025-12-31',
                'address': '123 Sample Street',
                'latitude': 22.123,
                'longitude': 114.123,
                'geo_address': 'Some Geo Address',
                'is_reserved': False,
                'average_rating': 4.5,
                'rating_count': 2,
                'universities': ['HKU']  # Added this required field
            },
            response_only=True
        )
    ]
)
class AccommodationSerializer(serializers.ModelSerializer):
    universities = serializers.SlugRelatedField(
        many=True,
        queryset=University.objects.all(),
        slug_field='code'
    )
    
    class Meta:
        model = Accommodation
        fields = '__all__'
        read_only_fields = [
            'latitude', 'longitude', 'geo_address',
            'is_reserved', 'average_rating', 'rating_count'
        ]

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Create Reservation Request (existing student)',
            value={
                "student": 1,
                "accommodation": 1,
                "reservation_start": "2025-07-01",
                "reservation_end": "2025-12-31",
                "status": "pending",
                # The following fields are ignored if student exists
                "student_name_input": "",
                "student_email": "",
                "student_contact": "",
                "student_campus": ""
            },
            request_only=True,
        ),
        OpenApiExample(
            'Create Reservation Request (new student)',
            value={
                "student": 9999,
                "student_name_input": "Alice Example",
                "student_email": "alice@example.com",
                "student_contact": "91234567",
                "student_campus": 2,
                "accommodation": 1,
                "reservation_start": "2025-07-01",
                "reservation_end": "2025-12-31",
                "status": "pending"
            },
            request_only=True,
        ),
        OpenApiExample(
            'Patch Reservation date Request',
            value={
                "reservation_start": "2025-07-01",
                "reservation_end": "2025-12-31",
            },
            request_only=True,
        ),
        OpenApiExample(
            'Reservation Response',
            value={
                "id": 1,
                "student": {
                    "id": 1,
                    "name": "John Smith",
                    "email": "john.smith@connect.hku.hk",
                    "contact": "98765432",
                    "campus": 1,
                    "campus_name": "HKU Main Campus"
                },
                "accommodation": 1,
                "accommodation_str": "Ocean Shores Tower 13 Floor 13 Flat A",
                "status": "pending",
                "reservation_start": "2025-07-01",
                "reservation_end": "2025-12-31",
                "created_at": "2025-05-01T10:00:00Z",
                "is_reserved": True
            },
            response_only=True
        )
    ]
)

class ReservationSerializer(serializers.ModelSerializer):

    student = serializers.IntegerField(write_only=True)
    student_obj = StudentSerializer(source='student', read_only=True)
    student_name = serializers.CharField(
        source='student.name', 
        read_only=True,
        help_text="Name of the student making the reservation"
    )
    student_name_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    student_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    student_contact = serializers.CharField(write_only=True, required=False, allow_blank=True)
    student_campus = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    accommodation_str = serializers.CharField(
        source='accommodation.__str__', 
        read_only=True,
        help_text="String representation of the accommodation"
    )
    is_reserved = serializers.BooleanField(
        source='accommodation.is_reserved',
        read_only=True,
        help_text="Current reservation status of the accommodation"
    )

    # student_name = serializers.CharField(write_only=True, required=False)
    # student_email = serializers.EmailField(write_only=True, required=False)
    # student_contact = serializers.CharField(write_only=True, required=False)
    # student_campus = serializers.IntegerField(write_only=True, required=False)

    def create(self, validated_data):
        # Remove extra fields not in the Reservation model
        validated_data.pop('student_name_input', None)
        validated_data.pop('student_email', None)
        validated_data.pop('student_contact', None)
        validated_data.pop('student_campus', None)
        return super().create(validated_data)
    
    def to_internal_value(self, data):
        if data.get('student_campus', None) == "":
            data['student_campus'] = None
        return super().to_internal_value(data)

    class Meta:
        model = Reservation
        fields = [
            'id', 'student', 'student_obj', 'student_name',
            'student_name_input', 'student_email', 'student_contact', 'student_campus',
            'accommodation', 'accommodation_str',
            'status', 'reservation_start', 'reservation_end',
            'created_at', 'is_reserved'
        ]
        read_only_fields = ['student_obj', 'student_name', 'accommodation_str', 'created_at', 'is_reserved']

class RatingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    accommodation_str = serializers.CharField(source='accommodation.__str__', read_only=True)

    class Meta:
        model = Rating
        fields = '__all__' # Includes student, accommodation IDs
        read_only_fields = ['student_name', 'accommodation_str', 'date']

# @extend_schema_serializer(
#     examples=[
#         OpenApiExample(
#             'Search Result Example',
#             value={
#                 "id": 1,
#                 "universities": ["HKU", "CUHK"],  # Updated to show multiple universities
#                 "building_name": "Ocean Shores",
#                 "type": "Flat",
#                 "beds": 2,
#                 "bedrooms": 1,
#                 "price": "1500.00",
#                 "latitude": 22.123,
#                 "longitude": 114.123,
#                 "address": "123 Sample Street",
#                 "distance": "1.5"
#             },
#             response_only=True
#         )
#     ]
# )
class AccommodationSearchSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField(
        help_text="Distance from specified campus in kilometers"
    )
    # Add a serializer field for universities
    universities = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='code'
    )
    
    class Meta:
        model = Accommodation
        fields = [
            'id', 'universities', 'availability_start', 'availability_end',  # Changed 'university' to 'universities'
            'type', 'beds', 'bedrooms', 'price', 'building_name',
            'latitude', 'longitude', 'address', 'distance'
        ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_distance(self, obj):
        """Get the stored distance for the current campus"""
        campus_id = self.context.get('campus_id')
        if not campus_id:
            return None
        
        try:
            distance_obj = obj.distances.get(campus_id=campus_id)
            return f"{distance_obj.distance:.1f}"
        except AccommodationDistance.DoesNotExist:
            return None
        
class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['code', 'name']