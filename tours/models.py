import secrets
from datetime import timedelta
from decimal import Decimal

from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.urls import reverse
from django.utils import timezone

from destinations.models import Destination, Place, TripStyle
from main.mixins import OptimisedImages, Page, TimeStamped


class Currency(models.TextChoices):
    USD = 'USD', 'US$'
    EUR = 'EUR', '€'
    GBP = 'GBP', '£'
    UGX = 'UGX', 'UGX'


class ItineraryQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Itinerary(Page):
    """A sellable trip.

    Two formats share this model:
    * day-by-day: a fixed programme described by its ``days``;
    * flexible: an open, tailor-able trip described by ``overview`` and its
      highlight ``places``, not locked to a daily schedule.

    Either format can have scheduled ``departures`` that travellers reserve
    seats on (group trips looking for people to join).
    """

    class Format(models.TextChoices):
        DAY_BY_DAY = 'day_by_day', 'Day-by-day itinerary'
        FLEXIBLE = 'flexible', 'Flexible / open itinerary'

    name = models.CharField(max_length=120)
    format = models.CharField(
        max_length=20, choices=Format.choices, default=Format.DAY_BY_DAY,
        help_text='Day-by-day trips list each day below. Flexible trips use the overview and highlights instead.',
    )
    summary = models.TextField(help_text='One or two sentences for cards and search results.')
    overview = RichTextField(blank=True, help_text='The full description. For flexible trips this is the main content.')
    cover = models.ImageField(upload_to='tours/')

    destinations = models.ManyToManyField(Destination, related_name='itineraries')
    styles = models.ManyToManyField(TripStyle, blank=True, related_name='itineraries')
    places = models.ManyToManyField(Place, blank=True, related_name='itineraries', verbose_name='highlights')

    duration_days = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)],
        help_text='Length in days. For flexible trips, the typical length.',
    )
    duration_note = models.CharField(
        max_length=60, blank=True,
        help_text='Optional text replacing the length, e.g. "5 to 9 days, you choose".',
    )
    price_from = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Starting price per person. Leave blank to show "Price on request".',
    )
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    price_note = models.CharField(max_length=80, blank=True, default='per person sharing')
    inclusions = models.TextField(blank=True, help_text="What's included, one item per line.")
    exclusions = models.TextField(blank=True, help_text="What's not included, one item per line.")

    is_featured = models.BooleanField(default=False, help_text='Show on the home page.')
    order = models.PositiveSmallIntegerField(default=0)

    image_fields = ('cover',)
    objects = ItineraryQuerySet.as_manager()

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'itinerary'
        verbose_name_plural = 'itineraries'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tours:detail', kwargs={'slug': self.slug})

    @property
    def is_day_by_day(self):
        return self.format == self.Format.DAY_BY_DAY

    @property
    def duration_label(self):
        if self.duration_note:
            return self.duration_note
        if self.duration_days:
            return f'{self.duration_days} day{"s" if self.duration_days != 1 else ""}'
        return 'Flexible length'

    @property
    def inclusions_list(self):
        return [line.strip(' -•\t') for line in self.inclusions.splitlines() if line.strip(' -•\t')]

    @property
    def exclusions_list(self):
        return [line.strip(' -•\t') for line in self.exclusions.splitlines() if line.strip(' -•\t')]

    def upcoming_departures(self):
        return self.departures.upcoming()


class Day(OptimisedImages):
    """One step of a day-by-day itinerary. A step can span several days."""
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    day_from = models.PositiveSmallIntegerField('day', validators=[MinValueValidator(1)])
    day_to = models.PositiveSmallIntegerField(
        'to day', null=True, blank=True,
        help_text='Optional. Fill in if this step covers several days (e.g. day 3 to 4).',
    )
    title = models.CharField(max_length=120)
    description = RichTextField(blank=True)
    image = models.ImageField(upload_to='tours/days/', blank=True)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    accommodation = models.CharField(max_length=120, blank=True)
    breakfast = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    dinner = models.BooleanField(default=False)

    image_fields = ('image',)

    class Meta:
        ordering = ['day_from', 'id']

    def __str__(self):
        return f'{self.label}: {self.title}'

    def clean(self):
        if self.day_to and self.day_to < self.day_from:
            raise ValidationError({'day_to': '"To day" must be after "day".'})

    @property
    def label(self):
        if self.day_to and self.day_to != self.day_from:
            return f'Days {self.day_from}–{self.day_to}'
        return f'Day {self.day_from}'

    @property
    def meals(self):
        return [name for name, on in (('Breakfast', self.breakfast), ('Lunch', self.lunch), ('Dinner', self.dinner)) if on]


# Reservations in these states hold seats on a departure.
HOLDING_STATUSES = ('pending', 'confirmed', 'deposit', 'paid')


class DepartureQuerySet(models.QuerySet):
    def with_seats(self):
        return self.annotate(
            seats_held=Sum('reservations__travellers', filter=Q(reservations__status__in=HOLDING_STATUSES)),
        )

    def upcoming(self):
        return (
            self.filter(is_published=True, start_date__gt=timezone.localdate())
            .exclude(status=Departure.Status.CANCELLED)
            .order_by('start_date')
        )


class Departure(TimeStamped):
    """A scheduled date for an itinerary that travellers can reserve seats on."""

    class Status(models.TextChoices):
        OPEN = 'open', 'Open for booking'
        GUARANTEED = 'guaranteed', 'Guaranteed to run'
        CLOSED = 'closed', 'Closed'
        CANCELLED = 'cancelled', 'Cancelled'

    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='departures')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank to work it out from the trip's length.")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Per person. Leave blank to use the itinerary's starting price.",
    )
    seats_total = models.PositiveSmallIntegerField('seats', default=12, validators=[MinValueValidator(1)])
    min_travellers = models.PositiveSmallIntegerField(
        default=2, validators=[MinValueValidator(1)],
        help_text='Bookings needed for the trip to run.',
    )
    booking_deadline = models.DateField(null=True, blank=True, help_text='Optional. Last day to reserve.')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    notes = models.CharField(max_length=200, blank=True, help_text='Shown to travellers, e.g. "Includes gorilla permit".')
    is_published = models.BooleanField(default=True)

    objects = DepartureQuerySet.as_manager()

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f'{self.itinerary.name}, {self.start_date:%d %b %Y}'

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date must be after the start date.'})
        if self.booking_deadline and self.booking_deadline > self.start_date:
            raise ValidationError({'booking_deadline': 'The deadline must be on or before the start date.'})

    def save(self, *args, **kwargs):
        if not self.end_date and self.start_date and self.itinerary_id and self.itinerary.duration_days:
            self.end_date = self.start_date + timedelta(days=self.itinerary.duration_days - 1)
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        return self.price if self.price is not None else self.itinerary.price_from

    @property
    def currency(self):
        return self.itinerary.currency

    @property
    def seats_reserved(self):
        held = getattr(self, 'seats_held', None)
        if held is None:
            held = self.reservations.filter(status__in=HOLDING_STATUSES).aggregate(n=Sum('travellers'))['n']
        return held or 0

    @property
    def seats_left(self):
        return max(self.seats_total - self.seats_reserved, 0)

    @property
    def is_bookable(self):
        today = timezone.localdate()
        return (
            self.is_published
            and self.status in (self.Status.OPEN, self.Status.GUARANTEED)
            and self.start_date > today
            and (self.booking_deadline is None or self.booking_deadline >= today)
            and self.seats_left > 0
        )

    def get_reserve_url(self):
        return reverse('tours:reserve', kwargs={'slug': self.itinerary.slug, 'pk': self.pk})


def make_reference():
    # Unambiguous characters only (no 0/O, 1/I) so it reads well over the phone.
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return 'KZ-' + ''.join(secrets.choice(alphabet) for _ in range(6))


class Reservation(TimeStamped):
    """A traveller's seat request on a departure. Payment is collected offline."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending: awaiting our confirmation'
        CONFIRMED = 'confirmed', 'Confirmed: awaiting payment'
        DEPOSIT = 'deposit', 'Deposit paid'
        PAID = 'paid', 'Paid in full'
        CANCELLED = 'cancelled', 'Cancelled'

    reference = models.CharField(max_length=12, unique=True, editable=False)
    departure = models.ForeignKey(Departure, on_delete=models.PROTECT, related_name='reservations')
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    country = models.CharField('country of residence', max_length=80, blank=True)
    travellers = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    staff_notes = models.TextField(blank=True, help_text='Internal: payment references, special requests...')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} {self.full_name}'

    def save(self, *args, **kwargs):
        if not self.reference:
            ref = make_reference()
            while Reservation.objects.filter(reference=ref).exists():
                ref = make_reference()
            self.reference = ref
        if self.amount_due is None and self.departure_id:
            price = self.departure.effective_price
            if price is not None:
                self.amount_due = price * self.travellers
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return (self.amount_due or 0) - self.amount_paid
