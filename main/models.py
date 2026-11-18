import re

from ckeditor.fields import RichTextField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from main.mixins import OptimisedImages, TimeStamped


class SiteSettings(models.Model):
    """Single row of business details edited in the admin and used site-wide."""
    site_name = models.CharField(max_length=60, default='Kaizen Safaris')
    tagline = models.CharField(max_length=160, default='Safaris, gorilla treks and tailor-made tours in Uganda and East Africa')
    description = models.CharField(
        'default SEO description', max_length=160,
        default='Kaizen Safaris is a Uganda-based tour operator offering gorilla trekking, wildlife safaris, '
                'honeymoons and tailor-made trips across East Africa.',
    )
    email = models.EmailField(default='info@kaizensafaris.com')
    phone = models.CharField('office phone', max_length=40, default='+256 393 243 933')
    whatsapp = models.CharField(max_length=40, default='+256 755 312 238', help_text='International format, e.g. +256 755 312 238.')
    address_line1 = models.CharField(max_length=120, default='Mukasa Towers, Ground Floor')
    address_line2 = models.CharField(max_length=120, default='Seeta – Namilyango Road', blank=True)
    city = models.CharField(max_length=60, default='Mukono')
    po_box = models.CharField(max_length=60, default='P O Box 8437', blank=True)
    country = models.CharField(max_length=60, default='Uganda')
    map_url = models.URLField('Google Maps link', blank=True)

    facebook = models.URLField(blank=True, default='https://www.facebook.com/kaizensafaris')
    instagram = models.URLField(blank=True, default='https://www.instagram.com/kaizensafarisug/')
    x = models.URLField('X (Twitter)', blank=True, default='https://x.com/KaizenSafaris')
    linkedin = models.URLField(blank=True, default='https://www.linkedin.com/in/kaizen-safaris-8a7845199/')
    youtube = models.URLField(blank=True, default='https://www.youtube.com/@kaizensafaris')
    tripadvisor = models.URLField(blank=True)

    payment_instructions = RichTextField(
        blank=True,
        help_text='Shown after a traveller reserves a seat: mobile money numbers, bank details, deposit policy.',
    )

    class Meta:
        verbose_name = 'site settings'
        verbose_name_plural = 'site settings'

    def __str__(self):
        return 'Site settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_digits(self):
        return re.sub(r'\D', '', self.whatsapp)

    @property
    def phone_digits(self):
        return '+' + re.sub(r'\D', '', self.phone)

    @property
    def social_links(self):
        pairs = [
            ('Facebook', 'fa-brands fa-facebook-f', self.facebook),
            ('Instagram', 'fa-brands fa-instagram', self.instagram),
            ('X', 'fa-brands fa-x-twitter', self.x),
            ('LinkedIn', 'fa-brands fa-linkedin-in', self.linkedin),
            ('YouTube', 'fa-brands fa-youtube', self.youtube),
            ('Tripadvisor', 'fa-brands fa-tripadvisor', self.tripadvisor),
        ]
        return [(label, icon, url) for label, icon, url in pairs if url]


class Review(TimeStamped):
    name = models.CharField(max_length=80)
    country = models.CharField(max_length=60, blank=True)
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    itinerary = models.ForeignKey('tours.Itinerary', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    source = models.CharField(max_length=60, blank=True, help_text='Where it was posted, e.g. SafariBookings, Google.')
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.rating}★)'


class Photo(TimeStamped, OptimisedImages):
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=160, blank=True)
    destination = models.ForeignKey('destinations.Destination', on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    order = models.PositiveSmallIntegerField(default=0)

    image_fields = ('image',)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'gallery photo'

    def __str__(self):
        return self.caption or f'Photo {self.pk}'


class Video(models.Model):
    title = models.CharField(max_length=120)
    url = models.URLField('YouTube link')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'gallery video'

    def __str__(self):
        return self.title

    @property
    def youtube_id(self):
        match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})', self.url)
        return match.group(1) if match else ''
