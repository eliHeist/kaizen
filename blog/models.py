import math

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from destinations.models import Destination, Place
from main.mixins import OptimisedImages, Page, SeoFields, Slugged
from tours.models import Itinerary


class Author(Slugged, OptimisedImages):
    name = models.CharField(max_length=80)
    role = models.CharField(max_length=80, blank=True, help_text='e.g. "Senior safari guide".')
    photo = models.ImageField(upload_to='blog/authors/', blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)

    image_fields = ('photo',)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:author', kwargs={'slug': self.slug})


class Category(Slugged, SeoFields):
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class Tag(Slugged):
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED, is_published=True, published_at__lte=timezone.now())


class Post(Page):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text='Posts dated in the future stay hidden until then.',
    )
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    excerpt = models.TextField(max_length=300, help_text='One or two sentences for cards and search results.')
    body = RichTextUploadingField()
    cover = models.ImageField(upload_to='blog/')
    is_featured = models.BooleanField(default=False)

    destinations = models.ManyToManyField(Destination, blank=True, related_name='posts')
    places = models.ManyToManyField(Place, blank=True, related_name='posts')
    itineraries = models.ManyToManyField(
        Itinerary, blank=True, related_name='posts',
        help_text='Shown as "Plan this trip" cards at the end of the post.',
    )

    slug_source = 'title'
    image_fields = ('cover',)
    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    @property
    def reading_minutes(self):
        words = len(strip_tags(self.body or '').split())
        return max(1, math.ceil(words / 220))
