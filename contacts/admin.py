from django.contrib import admin
from django.utils.html import format_html_join

from contacts.models import Enquiry, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active')
    list_editable = ('is_active',)


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'itinerary', 'travel_date', 'status', 'created_at')
    list_filter = ('kind', 'status', 'created_at')
    list_editable = ('status',)
    search_fields = ('name', 'email', 'phone', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('kind', 'name', 'email', 'phone', 'message', 'itinerary', 'travel_date', 'travellers',
                       'details_table', 'page_url', 'created_at')
    fields = ('status', 'kind', 'name', 'email', 'phone', 'itinerary', 'travel_date', 'travellers',
              'message', 'details_table', 'page_url', 'created_at', 'staff_notes')

    @admin.display(description='Other answers')
    def details_table(self, obj):
        if not obj.details:
            return '—'
        return format_html_join(
            '', '<div><strong>{}:</strong> {}</div>',
            ((k.replace('_', ' ').capitalize(), ', '.join(v) if isinstance(v, list) else v) for k, v in obj.details.items()),
        )

    def has_add_permission(self, request):
        return False
