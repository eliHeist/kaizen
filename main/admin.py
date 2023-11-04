from django.contrib import admin

from main.models import Equipment, EquipmentType, HoneymoonImages, HoneymoonSpot, Photo, Review, TopSpot, YTVideo

# Register your models here.
# admin.site.register(Equipment)
admin.site.register(Review)
admin.site.register(TopSpot)

class InlineEquipment(admin.StackedInline):
    model = Equipment
    extra = 1
    show_change_link = True
    can_delete = True


@admin.register(EquipmentType)
class ItineraryAdmin(admin.ModelAdmin):
    inlines = [InlineEquipment]

class InlineHoneymoonImages(admin.TabularInline):
    model = HoneymoonImages
    extra = 0
    show_change_link = True
    can_delete = True

@admin.register(HoneymoonSpot)
class HoneymoonSpotAdmin(admin.ModelAdmin):
    inlines = [InlineHoneymoonImages]


admin.site.register(Photo)
admin.site.register(YTVideo)