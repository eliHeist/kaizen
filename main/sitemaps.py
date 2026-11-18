from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Category, Post
from destinations.models import Destination, Place, TripStyle
from tours.models import Itinerary


class BaseSitemap(Sitemap):
    protocol = 'https'

    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None)


class StaticSitemap(BaseSitemap):
    names = {
        'main:home': 1.0,
        'tours:list': 0.9,
        'tours:departures': 0.8,
        'destinations:list': 0.8,
        'contacts:plan': 0.7,
        'rentals:list': 0.6,
        'blog:list': 0.7,
        'main:gallery': 0.4,
        'contacts:contact': 0.5,
    }

    def items(self):
        return list(self.names)

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.names[item]


class ModelSitemap(BaseSitemap):
    model = None
    priority = 0.6

    def items(self):
        return self.model.objects.published()


class DestinationSitemap(ModelSitemap):
    model = Destination
    priority = 0.8


class PlaceSitemap(ModelSitemap):
    model = Place

    def items(self):
        return Place.objects.published().filter(destination__is_published=True).select_related('destination')


class StyleSitemap(ModelSitemap):
    model = TripStyle
    priority = 0.7


class TourSitemap(ModelSitemap):
    model = Itinerary
    priority = 0.9


class PostSitemap(ModelSitemap):
    model = Post
    priority = 0.6


class CategorySitemap(BaseSitemap):
    priority = 0.4

    def items(self):
        return Category.objects.filter(posts__in=Post.objects.published()).distinct()


sitemaps = {
    'static': StaticSitemap,
    'destinations': DestinationSitemap,
    'places': PlaceSitemap,
    'styles': StyleSitemap,
    'tours': TourSitemap,
    'blog': PostSitemap,
    'blog-categories': CategorySitemap,
}
