from django.db import models

from main.currency import Prices
from main.mixins import OptimisedImages, Slugged


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
    price_usd = models.DecimalField('price (US$)', max_digits=10, decimal_places=2, null=True, blank=True)
    price_ugx = models.DecimalField(
        'price (UGX)', max_digits=14, decimal_places=0, null=True, blank=True,
        help_text='Leave both prices blank for "Price on request".',
    )
    price_unit = models.CharField(max_length=30, default='per day')
    is_available = models.BooleanField(default=True, help_text='Untick to hide it from the rentals page.')
    order = models.PositiveSmallIntegerField(default=0)

    image_fields = ('image',)

    class Meta:
        ordering = ['category__order', 'order', 'name']
        verbose_name = 'rental item'

    def __str__(self):
        return self.name

    @property
    def price(self):
        return Prices(self.price_usd, self.price_ugx)
