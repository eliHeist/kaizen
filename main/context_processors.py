from django.conf import settings

from destinations.models import Destination, TripStyle
from main import seo
from main.models import SiteSettings


def site(request):
    """Business details, navigation and organisation markup for every template."""
    settings_obj = SiteSettings.load()
    return {
        'site': settings_obj,
        'SITE_URL': settings.SITE_URL,
        'nav_destinations': Destination.objects.published().only('name', 'slug'),
        'nav_styles': TripStyle.objects.published().only('name', 'slug'),
        'org_jsonld': seo.organization(settings_obj),
    }
