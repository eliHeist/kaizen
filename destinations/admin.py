from django.contrib import admin
from django.utils.html import format_html

from destinations.models import Destination, Place, PlaceImage, TripStyle

SEO_FIELDSET = ('Search engines', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)})


def thumb(image, size=60):
    if not image:
        return '—'
    return format_html('<img src="{}" style="height:{}px;width:auto;border-radius:4px">', image.url, size)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'place_count', 'order', 'is_published')
    list_editable = ('order', 'is_published')
    search_fields = ('name', 'summary')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'tagline', 'summary', 'body', 'best_time_to_visit')}),
        ('Media', {'fields': ('cover', 'hero_video')}),
        ('Publishing', {'fields': ('order', 'is_published')}),
        SEO_FIELDSET,
    )

    @admin.display(description='Cover')
    def preview(self, obj):
        return thumb(obj.cover)

    @admin.display(description='Places')
    def place_count(self, obj):
        return obj.places.count()


@admin.register(TripStyle)
class TripStyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order', 'is_published')
    list_editable = ('order', 'is_published')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'summary', 'body', 'cover', 'icon')}),
        ('Publishing', {'fields': ('order', 'is_published')}),
        SEO_FIELDSET,
    )


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1
    fields = ('preview', 'image', 'caption', 'order')
    readonly_fields = ('preview',)

    @admin.display(description='')
    def preview(self, obj):
        return thumb(obj.image)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'destination', 'kind', 'is_featured', 'is_published')
    list_editable = ('is_featured', 'is_published')
    list_filter = ('destination', 'kind', 'styles', 'is_featured', 'is_published')
    search_fields = ('name', 'summary')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('styles',)
    inlines = [PlaceImageInline]
    fieldsets = (
        (None, {'fields': ('destination', 'name', 'slug', 'kind', 'summary', 'body', 'cover', 'styles')}),
        ('Publishing', {'fields': ('is_featured', 'order', 'is_published')}),
        SEO_FIELDSET,
    )

    @admin.display(description='Cover')
    def preview(self, obj):
        return thumb(obj.cover)
