from django.contrib import admin

from main.models import Equipment, EquipmentType, Photo, Review, YTVideo

# Register your models here.
# admin.site.register(Equipment)
admin.site.register(Review)

class InlineEquipment(admin.StackedInline):
    model = Equipment
    extra = 1
    show_change_link = True
    can_delete = True


@admin.register(EquipmentType)
class ItineraryAdmin(admin.ModelAdmin):
    inlines = [InlineEquipment]


admin.site.register(Photo)
admin.site.register(YTVideo)