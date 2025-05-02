from django.shortcuts import render
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import (
    Accommodation, Campus, Reservation, Rating,
    Student, Specialist, AccommodationOffering, AccommodationDistance
)
from .serializers import (
    AccommodationSerializer, CampusSerializer, AccommodationSearchSerializer,
    ReservationSerializer, RatingSerializer, StudentSerializer, SpecialistSerializer
)
from .utils import get_location_details, calculate_distance, send_reservation_notification
from django.shortcuts import get_object_or_404
from .permissions import IsUniversitySystemAuthenticated, IsFromSameUniversity
from drf_spectacular.utils import (
    extend_schema, 
    extend_schema_view,
    OpenApiParameter, 
    OpenApiExample,
    OpenApiResponse,
    extend_schema_field
)
from drf_spectacular.types import OpenApiTypes
from api.models import Student, Campus
from datetime import datetime
import datetime

# --- Accommodation Views ---

@extend_schema_view(
    list=extend_schema(
        summary="List all accommodations",
        description="Returns a list of all available accommodations.",
        responses={
            200: OpenApiResponse(
                response=AccommodationSerializer,
                description="List of accommodations retrieved successfully",
                examples=[
                    OpenApiExample(
                        "Sample Response",
                        value=[{
                            "id": 1,
                            "building_name": "Ocean Shores",
                            "type": "Flat",
                            "beds": 2,
                            "price": "1500.00",
                            "is_reserved": False
                        }]
                    )
                ]
            )
        },
        tags=['Accommodations']
    ),
    create=extend_schema(
        summary="Create accommodation",
        description="Create a new accommodation listing with automatic geocoding.",
        request=AccommodationSerializer,
        responses={
            201: AccommodationSerializer,
            400: OpenApiResponse(
                description="Invalid input",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"building_name": ["Building name is required"]}
                    )
                ]
            )
        },
        tags=['Accommodations']
    )
)
class AccommodationListCreateView(generics.ListCreateAPIView):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [IsUniversitySystemAuthenticated]

    def perform_create(self, serializer):
        """
        Overrides the default create action to:
        1. Set the university from the API key
        2. Fetch location details
        3. Create distance records for all campuses
        """
        building_name = serializer.validated_data.get('building_name')
        if not building_name:
            raise serializers.ValidationError({'building_name': 'Building name is required.'})

        # Call the utility function to get location data
        location_data = get_location_details(building_name)

        if location_data:
            # Save with university from API key
            accommodation = serializer.save(
                university=self.request.university,
                latitude=location_data['latitude'],
                longitude=location_data['longitude'],
                geo_address=location_data['geo_address']
            )

            # Calculate and store distances for all campuses
            campuses = Campus.objects.all()
            for campus in campuses:
                distance = calculate_distance(
                    accommodation.latitude, accommodation.longitude,
                    campus.latitude, campus.longitude
                )
                AccommodationDistance.objects.create(
                    accommodation=accommodation,
                    campus=campus,
                    distance=distance or float('inf')
                )
        else:
            raise serializers.ValidationError({
                'building_name': f"Could not retrieve location details for '{building_name}'. Please check the name or try again later."
            })

@extend_schema_view(
    retrieve=extend_schema(
        summary="Get accommodation details",
        description="Retrieve details of a specific accommodation by ID",
        responses={
            200: AccommodationSerializer,
            404: OpenApiResponse(description="Accommodation not found")
        },
        tags=['Accommodations']
    ),
    update=extend_schema(
        summary="Update accommodation",
        description="Update all fields of an existing accommodation",
        request=AccommodationSerializer,
        responses={
            200: AccommodationSerializer,
            404: OpenApiResponse(description="Accommodation not found"),
            400: OpenApiResponse(description="Invalid data")
        },
        tags=['Accommodations']
    ),
    destroy=extend_schema(
        summary="Delete accommodation",
        description="Delete an existing accommodation",
        responses={204: None},
        tags=['Accommodations']
    )
)
class AccommodationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single accommodation instance.
    GET: Returns details of a specific accommodation by ID.
    PUT/PATCH: Updates details of a specific accommodation.
    DELETE: Deletes a specific accommodation.
    """
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    # Add permissions later

# --- Campus Views ---

class CampusListCreateView(generics.ListCreateAPIView):
    """
    API view to list all campuses or create a new one.
    (Creation might be restricted to admin/staff later)
    """
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    # Add permissions later

class CampusDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single campus instance.
    (Update/Delete might be restricted later)
    """
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    # Add permissions later

# --- New Search View ---
@extend_schema(
    operation_id="accommodation_search",
    summary="Search accommodations",
    description="""
    Search accommodations with optional filters:
    - campus_id: Sort by distance from this campus
    - max_price: Maximum monthly rent in HKD
    - min_beds: Minimum number of beds required
    - type: Type of accommodation (Room/Flat/Mini hall)
    """,
    parameters=[
        OpenApiParameter(
            name="campus_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter and sort by distance from this campus (Please check campus id by GET Campus)",
            required=False,
            examples=[
                OpenApiExample(
                    'HKU Main Campus',
                    value=4,
                    description='Sort by distance from HKU main campus'
                ),
                OpenApiExample(
                    'The Chinese University of Hong Kong Campus',
                    value=9,
                    description='Sort by distance from The Chinese University of Hong Kong Campus'
                )
            ]
        ),
        OpenApiParameter(
            name="max_price",
            type=OpenApiTypes.DECIMAL,
            location=OpenApiParameter.QUERY,
            description="Maximum monthly rent in HKD",
            required=False,
            examples=[
                OpenApiExample(
                    'Budget',
                    value=None,
                    description='Find accommodations under ?/month'
                )
            ]
        ),
        OpenApiParameter(
            name="min_beds",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Minimum number of beds required",
            required=False,
            examples=[
                OpenApiExample(
                    'Beds',
                    value=None,
                    description='Find accommodations with at least ? beds'
                )
            ]
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Type of accommodation",
            required=False,
            enum=["Room", "Flat", "Mini hall"],
            examples=[
                OpenApiExample(
                    'Room type',
                    value=None,
                    description='Search for flats only'
                )
            ]
        )
    ],
    responses={
        200: OpenApiResponse(
            response=AccommodationSearchSerializer,
            description="List of accommodations matching the search criteria",
            examples=[
                OpenApiExample(
                    'Search Results',
                    value=[{
                        "id": 1,
                        "university": "HKU",
                        "building_name": "Ocean Shores",
                        "type": "Flat",
                        "beds": 2,
                        "bedrooms": 1,
                        "price": "1500.00",
                        "latitude": 22.123,
                        "longitude": 114.123,
                        "address": "123 Sample Street",
                        "distance": "1.5"
                    }]
                )
            ]
        ),
        401: OpenApiResponse(
            description="Authentication failed",
            examples=[
                OpenApiExample(
                    'Missing API Key',
                    value={"detail": "Missing API key"},
                    description="No university API key provided"
                )
            ]
        )
    },
    tags=['Search']
)
class AccommodationSearchView(generics.ListAPIView):
    serializer_class = AccommodationSearchSerializer
    permission_classes = [IsUniversitySystemAuthenticated]

    def get_queryset(self):
        """Filter accommodations by requesting university and search parameters"""
        queryset = Accommodation.objects.filter(
            universities__code=self.request.university
            # university=self.request.university
            # Remove: , is_reserved=False
        )

        # Apply filters from query parameters
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))

        min_beds = self.request.query_params.get('min_beds')
        if min_beds:
            queryset = queryset.filter(beds__gte=int(min_beds))

        accommodation_type = self.request.query_params.get('type')
        if accommodation_type:
            queryset = queryset.filter(type=accommodation_type)
        
        # Sort by distance if campus_id provided
        campus_id = self.request.query_params.get('campus_id')
        if campus_id:
            try:
                queryset = queryset.filter(
                    distances__campus_id=campus_id
                ).order_by('distances__distance')
                self._current_campus_id = int(campus_id)
            except (ValueError, Campus.DoesNotExist):
                pass
        
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['campus_id'] = getattr(self, '_current_campus_id', None)
        return context

# --- Reservation Views ---
@extend_schema_view(
    list=extend_schema(
        summary="List all reservations",
        description="Get all reservations for the authenticated university",
        responses={200: ReservationSerializer},
        tags=['Reservations']
    ),
    create=extend_schema(
        summary="Create reservation",
        description="""
        Create a new reservation for an accommodation.
        The accommodation's is_reserved status will be automatically set to True.
        Only available accommodations can be reserved.
        """,
        request=ReservationSerializer,
        responses={
            201: ReservationSerializer,
            400: OpenApiResponse(
                description="Invalid request",
                examples=[
                    OpenApiExample(
                        "Already Reserved",
                        value={"accommodation": ["This accommodation is already reserved"]},
                        description="Accommodation is not available"
                    ),
                    OpenApiExample(
                        "Invalid University",
                        value={"accommodation": ["This accommodation is not available for your university"]},
                        description="Accommodation belongs to different university"
                    ),
                    OpenApiExample(
                        "Invalid Dates",
                        value={"reservation_end": ["End date must be after start date"]},
                        description="Invalid reservation dates"
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Authentication failed",
                examples=[
                    OpenApiExample(
                        'Unauthorized',
                        value={"detail": "Invalid API key"},
                        description="Missing or invalid university API key"
                    )
                ]
            )
        },
        tags=['Reservations']
    )
)

class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsUniversitySystemAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(accommodation__universities__code=self.request.university)

    def perform_create(self, serializer):
        data = serializer.validated_data
        student_id = data.get('student')
        student = None
        new_student_created = False

        # Try to get the student by ID
        if student_id:
            try:
                student = Student.objects.get(pk=student_id)
            except Student.DoesNotExist:
                # If not found, try to create a new student with provided info
                student_name = data.get('student_name_input')
                student_email = data.get('student_email')
                student_contact = data.get('student_contact')
                student_campus_id = data.get('student_campus')

                if not all([student_name, student_email, student_campus_id]):
                    raise serializers.ValidationError({
                        "student": "To create a new student, provide name, email and campus."
                    })
                try:
                    campus = Campus.objects.get(pk=student_campus_id)
                except Campus.DoesNotExist:
                    raise serializers.ValidationError({"student_campus": "Invalid campus ID."})

                student = Student.objects.create(
                    name=student_name,
                    email=student_email,
                    contact=student_contact,
                    campus=campus
                )
                new_student_created = True
        else:
            raise serializers.ValidationError({"student": "Student ID is required."})

        # Now create the reservation with the resolved student
        try:
            accommodation = data['accommodation']

            # Check if reservation dates are within accommodation availability
            start = data['reservation_start']
            end = data['reservation_end']
            if start < accommodation.availability_start or end > accommodation.availability_end:
                raise serializers.ValidationError({
                    'reservation_start': f"Reservation must be within accommodation's available period: {accommodation.availability_start} to {accommodation.availability_end}",
                    'reservation_end': f"Reservation must be within accommodation's available period: {accommodation.availability_start} to {accommodation.availability_end}",
                })

            # Check for overlapping reservations
            overlapping_reservations = Reservation.objects.filter(
                accommodation=accommodation,
                status__in=['pending', 'confirmed', 'contract_not_signed'],
            ).filter(
                reservation_start__lt=end,
                reservation_end__gt=start
            )
            
            if overlapping_reservations.exists():
                # Get the conflicting dates to show in the error message
                conflicts = []
                for res in overlapping_reservations:
                    conflicts.append(f"{res.reservation_start} to {res.reservation_end}")
                
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"This accommodation is already reserved during the requested period. " +
                        f"Conflicts with existing reservations: {', '.join(conflicts)}"
                    ]
                })

            # Check if accommodation belongs to university
            if self.request.university not in accommodation.universities.values_list('code', flat=True):
                raise serializers.ValidationError({
                    'accommodation': 'This accommodation is not available for your university.'
                })
            if Reservation.objects.filter(student=student, accommodation=accommodation).exists():
                raise serializers.ValidationError({
                    'accommodation': 'You have already reserved this accommodation.'
                })
            if end < start:
                raise serializers.ValidationError({
                    'reservation_end': 'End date must be after start date.'
                })

            reservation = serializer.save(student=student)
            send_reservation_notification(reservation)
        except Exception as e:
            # If a new student was created and an error occurs, delete the student
            if new_student_created and student is not None:
                student.delete()
            raise

@extend_schema_view(
    retrieve=extend_schema(
        summary="Get reservation details",
        description="Retrieve a specific reservation",
        responses={
            200: ReservationSerializer,
            404: OpenApiResponse(description="Reservation not found")
        },
        tags=['Reservations']
    ),
    partial_update=extend_schema(
        summary="Update reservation partially",
        description="""
        Update specific fields of a reservation. Fields can be:
        - status: Change reservation status
        - reservation_start: New start date
        - reservation_end: New end date
        Leave fields empty to keep original values.
        """,
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID of reservation to update",
                required=True
            ),
        ],
        request=ReservationSerializer,
        responses={
            200: ReservationSerializer,
            400: OpenApiResponse(
                description="Invalid update data",
                examples=[
                    OpenApiExample(
                        "Invalid Status",
                        value={"status": ["Invalid status choice"]},
                        description="Invalid status provided"
                    ),
                    OpenApiExample(
                        "Invalid Dates",
                        value={"reservation_end": ["End date must be after start date"]},
                        description="Invalid date range"
                    )
                ]
            ),
            404: OpenApiResponse(description="Reservation not found")
        },
        examples=[
            OpenApiExample(
                "Update Status",
                value={"status": "canceled"},
                description="Cancel a reservation"
            ),
            OpenApiExample(
                "Update Dates",
                value={
                    "reservation_start": "2025-10-01",
                    "reservation_end": "2025-12-31"
                },
                description="Change reservation dates"
            )
        ],
        tags=['Reservations']
    ),
    destroy=extend_schema(
        summary="Cancel reservation",
        description="Cancel and delete a reservation by ID",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID of reservation to cancel",
                required=True
            ),
        ],
        responses={
            204: OpenApiResponse(description="Reservation successfully canceled"),
            404: OpenApiResponse(description="Reservation not found")
        },
        tags=['Reservations']
    )
)
class ReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsUniversitySystemAuthenticated]
    http_method_names = ['get', 'patch', 'delete']  # Only allow PATCH for partial updates

    def get_queryset(self):
        """Filter reservations by university"""
        return Reservation.objects.filter(
            accommodation__universities__code=self.request.university
        )

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests to update specific fields"""
        instance = self.get_object()
        
        # Validate the reservation belongs to specialist's university
        if request.university not in instance.accommodation.universities.values_list('code', flat=True):
            raise serializers.ValidationError({
                "detail": "You can only update reservations for your university"
            })

        # If updating dates, validate them
        if 'reservation_start' in request.data or 'reservation_end' in request.data:
            # Convert string dates to datetime.date objects if they're strings
            start_date = request.data.get('reservation_start', instance.reservation_start)
            end_date = request.data.get('reservation_end', instance.reservation_end)

            # Handle string conversion if needed
            if isinstance(start_date, str):
                try:
                    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    raise serializers.ValidationError({
                        'reservation_start': 'Invalid date format. Use YYYY-MM-DD'
                    })

            if isinstance(end_date, str):
                try:
                    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    raise serializers.ValidationError({
                        'reservation_end': 'Invalid date format. Use YYYY-MM-DD'
                    })

            # Validate date range
            if end_date < start_date:
                raise serializers.ValidationError({
                    'reservation_end': 'End date must be after start date.'
                })

            # Validate against accommodation availability period
            if (start_date < instance.accommodation.availability_start or 
                end_date > instance.accommodation.availability_end):
                raise serializers.ValidationError({
                    'reservation_start': f"Reservation must be within accommodation's available period: {instance.accommodation.availability_start} to {instance.accommodation.availability_end}",
                    'reservation_end': f"Reservation must be within accommodation's available period: {instance.accommodation.availability_start} to {instance.accommodation.availability_end}"
                })
                
            # Check for overlapping reservations (excluding the current one)
            overlapping_reservations = Reservation.objects.filter(
                accommodation=instance.accommodation,
                status__in=['pending', 'confirmed', 'contract_not_signed'],
            ).exclude(
                pk=instance.pk  # Exclude the current reservation
            ).filter(
                reservation_start__lt=end_date,
                reservation_end__gt=start_date
            )
            
            if overlapping_reservations.exists():
                conflicts = []
                for res in overlapping_reservations:
                    conflicts.append(f"{res.reservation_start} to {res.reservation_end}")
                
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"This accommodation is already reserved during the requested period. " +
                        f"Conflicts with existing reservations: {', '.join(conflicts)}"
                    ]
                })

        # If status is being changed to 'canceled', trigger the cancellation logic
        if request.data.get('status') == 'canceled':
            instance.accommodation.is_reserved = False
            instance.accommodation.save()

        # Perform the partial update
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Send notification about the update
        send_reservation_notification(serializer.instance, action='update')

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Handle DELETE requests to cancel reservations"""
        instance = self.get_object()
        
        # Validate the reservation belongs to specialist's university
        if request.university not in instance.accommodation.universities.values_list('code', flat=True):
            raise serializers.ValidationError({
                "detail": "You can only update reservations for your university"
            })

        # Send notification before deleting
        send_reservation_notification(instance, action='delete')
        
        # Set accommodation as not reserved before deleting
        instance.accommodation.is_reserved = False
        instance.accommodation.save()
        
        # Delete the reservation
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- Rating Views ---

@extend_schema_view(
    list=extend_schema(
        summary="List ratings",
        description="Get all ratings, optionally filtered by accommodation",
        parameters=[
            OpenApiParameter(
                name="accommodation_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Filter ratings by accommodation ID",
                required=False
            )
        ],
        responses={200: RatingSerializer},
        tags=['Ratings']
    ),
    create=extend_schema(
        summary="Create rating",
        description="Create a new rating for an accommodation",
        request=RatingSerializer,
        responses={
            201: RatingSerializer,
            400: OpenApiResponse(
                description="Invalid rating",
                examples=[
                    OpenApiExample(
                        "Invalid Rating",
                        value={"rating": ["Rating must be between 0 and 5"]}
                    )
                ]
            )
        },
        tags=['Ratings']
    )
)
class RatingListCreateView(generics.ListCreateAPIView):
    """
    API view to list ratings or create a new one.
    Requires authentication.
    """
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Optionally filter ratings by accommodation ID if provided"""
        queryset = Rating.objects.all()
        accommodation_id = self.request.query_params.get('accommodation_id')
        if (accommodation_id):
            queryset = queryset.filter(accommodation__id=accommodation_id)
        return queryset

    def perform_create(self, serializer):
        # TODO: Set student based on authenticated user
        # serializer.save(student=self.request.user)
        serializer.save()

# Add views for Reservation, Rating, Student, Specialist, Offering later as needed

# --- Student Views ---
@extend_schema_view(
    list=extend_schema(
        summary="List all students",
        description="Get all students registered in the system",
        responses={
            200: OpenApiResponse(
                response=StudentSerializer,
                description="List of students retrieved successfully",
                examples=[
                    OpenApiExample(
                        'Student List',
                        value=[{
                            'id': 1,
                            'name': 'John Smith',
                            'email': 'john@example.com',
                            'contact': '12345678',
                            'campus': 1,
                            'campus_name': 'HKU Main Campus'
                        }]
                    )
                ]
            )
        },
        tags=['Students']
    ),
    create=extend_schema(
        summary="Register new student",
        description="Create a new student account",
        request=StudentSerializer,
        responses={
            201: OpenApiResponse(
                response=StudentSerializer,
                description="Student created successfully",
                examples=[
                    OpenApiExample(
                        'Created Student',
                        value={
                            'id': 1,
                            'name': 'John Smith',
                            'email': 'john@example.com',
                            'contact': '12345678',
                            'campus': 1,
                            'campus_name': 'HKU Main Campus'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid input",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "email": ["This email is already registered"],
                            "campus": ["This field is required"]
                        }
                    )
                ]
            )
        },
        tags=['Students']
    )
)
class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsUniversitySystemAuthenticated]

    def get_queryset(self):
        """Filter students by requesting university"""
        return Student.objects.filter(
            campus__university=self.request.university
        )

@extend_schema_view(
    retrieve=extend_schema(
        summary="Get student details",
        description="Retrieve details of a specific student",
        responses={
            200: StudentSerializer,
            404: OpenApiResponse(description="Student not found")
        },
        tags=['Students']
    ),
    update=extend_schema(
        summary="Update student",
        description="Update student information",
        request=StudentSerializer,
        responses={
            200: StudentSerializer,
            400: OpenApiResponse(description="Invalid data")
        },
        tags=['Students']
    ),
    destroy=extend_schema(
        summary="Delete student",
        description="Remove a student from the system",
        responses={204: None},
        tags=['Students']
    )
)
class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsUniversitySystemAuthenticated]

    def get_queryset(self):
        return Student.objects.filter(
            campus__university=self.request.university
        )

# --- Specialist Views ---
@extend_schema_view(
    list=extend_schema(
        summary="List all specialists",
        description="Get all accommodation specialists in the system",
        responses={
            200: OpenApiResponse(
                response=SpecialistSerializer,
                description="List of specialists retrieved successfully",
                examples=[
                    OpenApiExample(
                        'Specialist List',
                        value=[{
                            'id': 1,
                            'name': 'Jane Doe',
                            'email': 'jane@university.edu',
                            'contact': '87654321',
                            'campus': 1,
                            'campus_name': 'HKU Main Campus'
                        }]
                    )
                ]
            )
        },
        tags=['Specialists']
    ),
    create=extend_schema(
        summary="Register new specialist",
        description="Create a new accommodation specialist account",
        request=SpecialistSerializer,
        responses={
            201: OpenApiResponse(
                response=SpecialistSerializer,
                description="Specialist created successfully",
                examples=[
                    OpenApiExample(
                        'Created Specialist',
                        value={
                            'id': 1,
                            'name': 'Jane Doe',
                            'email': 'jane@university.edu',
                            'contact': '87654321',
                            'campus': 1,
                            'campus_name': 'HKU Main Campus'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid input",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "email": ["This email is already registered"],
                            "contact": ["This field is required"]
                        }
                    )
                ]
            )
        },
        tags=['Specialists']
    )
)
class SpecialistListCreateView(generics.ListCreateAPIView):
    serializer_class = SpecialistSerializer
    permission_classes = [IsUniversitySystemAuthenticated]

    def get_queryset(self):
        """Filter specialists by requesting university"""
        return Specialist.objects.filter(
            campus__university=self.request.university
        )

@extend_schema_view(
    retrieve=extend_schema(
        summary="Get specialist details",
        description="Retrieve details of a specific specialist",
        responses={
            200: SpecialistSerializer,
            404: OpenApiResponse(description="Specialist not found")
        },
        tags=['Specialists']
    ),
    update=extend_schema(
        summary="Update specialist",
        description="Update specialist information",
        request=SpecialistSerializer,
        responses={
            200: SpecialistSerializer,
            400: OpenApiResponse(description="Invalid data")
        },
        tags=['Specialists']
    ),
    destroy=extend_schema(
        summary="Delete specialist",
        description="Remove a specialist from the system",
        responses={204: None},
        tags=['Specialists']
    )
)
class SpecialistDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SpecialistSerializer
    permission_classes = [IsUniversitySystemAuthenticated]

    def get_queryset(self):
        return Specialist.objects.filter(
            campus__university=self.request.university
        )