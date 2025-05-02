from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Reservation, Rating, Accommodation, Campus, AccommodationDistance
from .utils import calculate_distance

@receiver(post_save, sender=Reservation)
def update_accommodation_reserved_on_save(sender, instance, created, **kwargs):
    """
    When a reservation is created or updated, set the accommodation's
    is_reserved flag to True if the status indicates reservation.
    Assumes 'pending', 'confirmed', 'contract_not_signed' mean reserved.
    """
    # Check if the reservation status implies the accommodation is taken
    # Adjust these statuses based on your workflow
    reserved_statuses = ['pending', 'confirmed', 'contract_not_signed']
    if instance.status in reserved_statuses:
        accommodation = instance.accommodation
        if not accommodation.is_reserved:
            accommodation.is_reserved = True
            accommodation.save(update_fields=['is_reserved'])
    #If status changes to 'canceled' or 'completed', trigger the delete logic (this is optional)
    elif instance.status in ['canceled', 'completed']:
         # Simulate delete logic to check if accommodation should become available
         update_accommodation_reserved_on_delete(sender, instance, **kwargs)


@receiver(post_delete, sender=Reservation)
def update_accommodation_reserved_on_delete(sender, instance, **kwargs):
    """
    When a reservation is deleted (or canceled/completed), check if any *other*
    active reservations exist for the same accommodation. If not,
    set its is_reserved flag to False.
    """
    accommodation = instance.accommodation
    # Check if other reservations exist for this accommodation
    reserved_statuses = ['pending', 'confirmed', 'contract_not_signed']
    other_reservations_exist = Reservation.objects.filter(
        accommodation=accommodation,
        status__in=reserved_statuses
    ).exclude(pk=instance.pk).exists() # Exclude the instance being deleted/processed

    if not other_reservations_exist and accommodation.is_reserved:
        accommodation.is_reserved = False
        accommodation.save(update_fields=['is_reserved'])


@receiver([post_save, post_delete], sender=Rating)
def update_accommodation_rating(sender, instance, **kwargs):
    """
    When a rating is saved or deleted, recalculate the average rating
    and rating count for the associated accommodation.
    """
    accommodation = instance.accommodation
    
    # Recalculate average and count using Django aggregation
    aggregates = Rating.objects.filter(accommodation=accommodation).aggregate(
        average_rating=Avg('rating'),
        rating_count=Count('id')
    )

    # Update the accommodation with new values
    accommodation.average_rating = aggregates['average_rating'] or 0.0
    accommodation.rating_count = aggregates['rating_count']
    accommodation.save()

    print(f"Updated ratings for Accommodation {accommodation.pk}: "
          f"Avg={accommodation.average_rating}, Count={accommodation.rating_count}")
    
@receiver(post_save, sender=Accommodation)
def calculate_accommodation_distances(sender, instance, created, **kwargs):
    """Calculate and store distances to all campuses when an accommodation is created/updated"""
    if created or instance.latitude != instance._original_latitude or instance.longitude != instance._original_longitude:
        # Get all campuses
        campuses = Campus.objects.all()
        
        # Calculate and store distance to each campus
        for campus in campuses:
            distance = calculate_distance(
                instance.latitude, instance.longitude,
                campus.latitude, campus.longitude
            )
            AccommodationDistance.objects.update_or_create(
                accommodation=instance,
                campus=campus,
                defaults={'distance': distance or float('inf')}
            )

@receiver(post_save, sender=Campus)
def calculate_campus_distances(sender, instance, created, **kwargs):
    """Calculate and store distances from all accommodations when a campus is created/updated"""
    if created or instance.latitude != instance._original_latitude or instance.longitude != instance._original_longitude:
        # Get all accommodations
        accommodations = Accommodation.objects.all()
        
        # Calculate and store distance from each accommodation
        for accommodation in accommodations:
            distance = calculate_distance(
                accommodation.latitude, accommodation.longitude,
                instance.latitude, instance.longitude
            )
            AccommodationDistance.objects.update_or_create(
                accommodation=accommodation,
                campus=instance,
                defaults={'distance': distance or float('inf')}
            )