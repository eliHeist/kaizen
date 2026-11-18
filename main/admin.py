from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from destinations.admin import thumb
from main.models import Photo, Review, SiteSettings, Video


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Business', {'fields': ('site_name', 'tagline', 'description')}),
        ('Contact', {'fields': ('email', 'phone', 'whatsapp')}),
        ('Address', {'fields': ('address_line1', 'address_line2', 'city', 'po_box', 'country', 'map_url')}),
        ('Social media', {'fields': ('facebook', 'instagram', 'x', 'linkedin', 'youtube', 'tripadvisor')}),
        ('Reservations', {'fields': ('payment_instructions',)}),
    )

    def changelist_view(self, request, extra_context=None):
        # There is only ever one settings row: go straight to editing it.
        obj = SiteSettings.load()
        return redirect(reverse('admin:main_sitesettings_change', args=[obj.pk]))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'rating', 'itinerary', 'source', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('rating', 'is_published', 'source')
    search_fields = ('name', 'text')
    autocomplete_fields = ('itinerary',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'preview', 'destination', 'order')
    list_editable = ('order',)
    list_filter = ('destination',)

    @admin.display(description='Photo')
    def preview(self, obj):
        return thumb(obj.image)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order')
    list_editable = ('order',)
