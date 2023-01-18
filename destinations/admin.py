from django.contrib import admin

from destinations.models import Day, Destination, Itinerary

# Register your models here.
admin.site.register(Destination)

class InlineDay(admin.StackedInline):
    model = Day
    extra = 1
    show_change_link = True
    can_delete = True


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    inlines = [InlineDay]
