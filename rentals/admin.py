from django.contrib import admin

from destinations.admin import thumb
from rentals.models import RentalCategory, RentalItem


class RentalItemInline(admin.StackedInline):
    model = RentalItem
    extra = 0
    fields = (('name', 'is_available'), 'image', 'summary', 'capacity', ('price', 'currency', 'price_unit'), 'order')


@admin.register(RentalCategory)
class RentalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_count', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RentalItemInline]

    @admin.display(description='Items')
    def item_count(self, obj):
        return obj.items.count()


@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'category', 'price', 'price_unit', 'is_available')
    list_editable = ('is_available',)
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'summary')

    @admin.display(description='Photo')
    def preview(self, obj):
        return thumb(obj.image)
