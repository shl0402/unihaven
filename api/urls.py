# File: api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Accommodation URLs
    path('accommodations/search/', views.AccommodationSearchView.as_view(), name='accommodation-search'),
    path('accommodations/', views.AccommodationListCreateView.as_view(), name='accommodation-list-create'),
    path('accommodations/<int:pk>/', views.AccommodationDetailView.as_view(), name='accommodation-detail'),

    # Campus URLs
    path('campuses/', views.CampusListCreateView.as_view(), name='campus-list-create'),
    path('campuses/<int:pk>/', views.CampusDetailView.as_view(), name='campus-detail'),

    # Reservation URLs
    path('reservations/', views.ReservationListCreateView.as_view(), name='reservation-list-create'),
    path('reservations/<int:pk>/', views.ReservationDetailView.as_view(), name='reservation-detail'),

    # Rating URLs
    path('ratings/', views.RatingListCreateView.as_view(), name='rating-list-create'),
    # path('ratings/<int:pk>/', views.RatingDetailView.as_view(), name='rating-detail'), # Optional

    # Add URLs for Student, Specialist, Offering later if direct manipulation is needed
    # Student URLs
    path('students/', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),

    # Specialist URLs
    path('specialists/', views.SpecialistListCreateView.as_view(), name='specialist-list-create'),
    path('specialists/<int:pk>/', views.SpecialistDetailView.as_view(), name='specialist-detail'),
]