from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from destinations.admin import SEO_FIELDSET, thumb
from tours.models import Day, Departure, Itinerary, Reservation


class DayInline(admin.StackedInline):
    model = Day
    extra = 0
    classes = ('collapse',)
    autocomplete_fields = ('place',)
    fields = (
        ('day_from', 'day_to'), 'title', 'description', 'image', 'place', 'accommodation',
        ('breakfast', 'lunch', 'dinner'),
    )
    verbose_name_plural = 'Days (for day-by-day itineraries)'


class DepartureInline(admin.TabularInline):
    model = Departure
    extra = 0
    fields = ('start_date', 'end_date', 'price_usd', 'price_ugx', 'seats_total', 'seats_left_display', 'status', 'is_published', 'manage')
    readonly_fields = ('seats_left_display', 'manage')
    show_change_link = False

    @admin.display(description='Seats left')
    def seats_left_display(self, obj):
        return obj.seats_left if obj.pk else '—'

    @admin.display(description='')
    def manage(self, obj):
        if not obj.pk:
            return ''
        url = reverse('admin:tours_departure_change', args=[obj.pk])
        return format_html('<a href="{}">Reservations →</a>', url)


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'format', 'duration_label', 'price_from_usd', 'price_from_ugx', 'next_departure', 'is_featured', 'is_published')
    list_editable = ('is_featured', 'is_published')
    list_filter = ('format', 'destinations', 'styles', 'is_featured', 'is_published')
    search_fields = ('name', 'summary')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('destinations', 'styles', 'places')
    inlines = [DepartureInline, DayInline]
    save_on_top = True
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'format', 'summary', 'cover', 'overview')}),
        ('Where and what', {'fields': ('destinations', 'styles', 'places')}),
        ('Length and price', {'fields': (
            ('duration_days', 'duration_note'), ('price_from_usd', 'price_from_ugx'), 'price_note', 'inclusions', 'exclusions',
        )}),
        ('Publishing', {'fields': ('is_featured', 'order', 'is_published')}),
        SEO_FIELDSET,
    )

    @admin.display(description='Cover')
    def preview(self, obj):
        return thumb(obj.cover)

    @admin.display(description='Next departure')
    def next_departure(self, obj):
        dep = obj.departures.upcoming().first()
        return f'{dep.start_date:%d %b %Y}' if dep else '—'


class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    fields = ('reference', 'full_name', 'travellers', 'status', 'currency', 'amount_due', 'amount_paid')
    readonly_fields = ('reference',)
    show_change_link = True


@admin.register(Departure)
class DepartureAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'start_date', 'end_date', 'price_usd', 'price_ugx', 'seats_total', 'seats_left_display', 'status', 'is_published')
    list_filter = ('status', 'is_published', 'itinerary')
    list_editable = ('status', 'is_published')
    search_fields = ('itinerary__name',)
    date_hierarchy = 'start_date'
    autocomplete_fields = ('itinerary',)
    inlines = [ReservationInline]

    def get_queryset(self, request):
        return super().get_queryset(request).with_seats().select_related('itinerary')

    @admin.display(description='Seats left')
    def seats_left_display(self, obj):
        return obj.seats_left


def _set_status(status, label):
    @admin.action(description=f'Mark selected as "{label}"')
    def action(modeladmin, request, queryset):
        n = queryset.update(status=status)
        modeladmin.message_user(request, f'{n} reservation(s) updated.', messages.SUCCESS)
    action.__name__ = f'mark_{status}'
    return action


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reference', 'full_name', 'departure', 'travellers', 'status', 'currency', 'amount_due', 'amount_paid', 'balance', 'created_at')
    list_filter = ('status', 'departure__itinerary', 'created_at')
    search_fields = ('reference', 'full_name', 'email', 'phone')
    readonly_fields = ('reference', 'created_at', 'updated_at', 'balance')
    autocomplete_fields = ('departure',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('reference', 'departure', 'status')}),
        ('Traveller', {'fields': ('full_name', 'email', 'phone', 'country', 'travellers', 'message')}),
        ('Payment (collected offline)', {'fields': ('currency', 'amount_due', 'amount_paid', 'balance', 'staff_notes')}),
        ('Record', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    actions = [
        _set_status(s, label) for s, label in (
            (Reservation.Status.CONFIRMED, 'Confirmed'),
            (Reservation.Status.DEPOSIT, 'Deposit paid'),
            (Reservation.Status.PAID, 'Paid in full'),
            (Reservation.Status.CANCELLED, 'Cancelled'),
        )
    ]
