from django.conf import settings

from destinations.models import Destination, TripStyle
from main.models import SiteSettings


def site(request):
    """Business details and navigation data available in every template."""
    return {
        'site': SiteSettings.load(),
        'SITE_URL': settings.SITE_URL,
        'nav_destinations': Destination.objects.published().only('name', 'slug'),
        'nav_styles': TripStyle.objects.published().only('name', 'slug'),
    }
