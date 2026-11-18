from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse

from main.mixins import OptimisedImages, Page


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Destination(Page):
    """A country or region we operate in (Uganda, Kenya, ...)."""
    name = models.CharField(max_length=60, unique=True)
    tagline = models.CharField(max_length=160, blank=True, help_text='One line shown under the name.')
    summary = models.TextField(help_text='Short intro used on cards and in search results.')
    body = RichTextField('About', blank=True)
    cover = models.ImageField(upload_to='destinations/')
    hero_video = models.FileField(upload_to='destinations/video/', blank=True, help_text='Optional MP4 shown behind the page title.')
    best_time_to_visit = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text='Lower numbers are listed first.')

    image_fields = ('cover',)
    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('destinations:detail', kwargs={'slug': self.slug})


class TripStyle(Page):
    """A way to travel: Honeymoon, Gorilla trekking, Family, Birding..."""
    name = models.CharField(max_length=60, unique=True)
    summary = models.TextField(blank=True)
    body = RichTextField(blank=True)
    cover = models.ImageField(upload_to='styles/', blank=True)
    icon = models.CharField(
        max_length=40, blank=True,
        help_text='Optional Font Awesome class, e.g. "fa-solid fa-heart". See fontawesome.com/icons.',
    )
    order = models.PositiveSmallIntegerField(default=0)

    image_fields = ('cover',)
    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'trip style'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tours:style', kwargs={'slug': self.slug})


class Place(Page):
    """A highlight within a destination: a park, lake, lodge area, city..."""

    class Kind(models.TextChoices):
        PARK = 'park', 'National park / reserve'
        WATER = 'water', 'Lake, river or waterfall'
        MOUNTAIN = 'mountain', 'Mountain or hills'
        BEACH = 'beach', 'Beach or island'
        CULTURE = 'culture', 'City, culture or heritage'
        OTHER = 'other', 'Other'

    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.PARK)
    summary = models.TextField(help_text='Short intro used on cards and in search results.')
    body = RichTextField('Description', blank=True)
    cover = models.ImageField(upload_to='places/')
    styles = models.ManyToManyField(
        TripStyle, blank=True, related_name='places',
        help_text='Trip styles this place is good for (e.g. Honeymoon).',
    )
    is_featured = models.BooleanField(default=False, help_text='Show on the home page.')
    order = models.PositiveSmallIntegerField(default=0)

    image_fields = ('cover',)
    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.destination})'

    def get_absolute_url(self):
        return reverse('destinations:place', kwargs={'destination': self.destination.slug, 'slug': self.slug})


class PlaceImage(OptimisedImages):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='places/gallery/')
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    image_fields = ('image',)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'gallery image'

    def __str__(self):
        return self.caption or f'{self.place.name} photo'
