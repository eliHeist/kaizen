from django.db import models

from main.mixins import OptimisedImages, Slugged
from tours.models import Currency


class RentalCategory(Slugged):
    """A group of hire items, e.g. "Safari vehicles" or "Camping gear"."""
    name = models.CharField(max_length=60, unique=True)
    summary = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True, help_text='Optional Font Awesome class, e.g. "fa-solid fa-car".')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'rental category'
        verbose_name_plural = 'rental categories'

    def __str__(self):
        return self.name


class RentalItem(OptimisedImages):
    category = models.ForeignKey(RentalCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=80)
    image = models.ImageField(upload_to='rentals/')
    summary = models.TextField(blank=True)
    capacity = models.CharField(max_length=60, blank=True, help_text='e.g. "7 seats, pop-up roof" or "Sleeps 3".')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Leave blank for "Price on request".')
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    price_unit = models.CharField(max_length=30, default='per day')
    is_available = models.BooleanField(default=True, help_text='Untick to hide it from the rentals page.')
    order = models.PositiveSmallIntegerField(default=0)

    image_fields = ('image',)

    class Meta:
        ordering = ['category__order', 'order', 'name']
        verbose_name = 'rental item'

    def __str__(self):
        return self.name
