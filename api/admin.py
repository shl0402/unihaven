from django.contrib import admin
from .models import Campus, Student, Specialist, Accommodation, AccommodationOffering, Reservation, Rating, AccommodationDistance, University

class AccommodationDistanceInline(admin.TabularInline):
    model = AccommodationDistance
    extra = 0

@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    inlines = [AccommodationDistanceInline]
    list_display = ['building_name', 'type', 'beds', 'price', 'get_universities']
    filter_horizontal = ['universities']  # Makes it easier to select multiple universities
    
    def get_universities(self, obj):
        return ", ".join([university.code for university in obj.universities.all()])
    get_universities.short_description = 'Universities'

admin.site.register(University)
# admin.site.register(Accommodation, AccommodationAdmin)
admin.site.register(AccommodationDistance)
admin.site.register(Campus)
admin.site.register(Student)
admin.site.register(Specialist)
# admin.site.register(AccommodationOffering)
admin.site.register(Reservation)
admin.site.register(Rating)