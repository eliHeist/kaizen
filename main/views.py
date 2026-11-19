from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST

from blog.models import Post
from destinations.models import Destination, Place, TripStyle
from main import currency as money
from main.models import Photo, Review, Video
from tours.models import Departure, Itinerary


PARTNER_LOGOS = [
    ('img/affiliations/safaribookings.webp', 'SafariBookings'),
    ('img/affiliations/auto.webp', 'Association of Uganda Tour Operators'),
    ('img/affiliations/uwa.webp', 'Uganda Wildlife Authority'),
    ('img/affiliations/uta.webp', 'Uganda Tourism Association'),
    ('img/affiliations/utb.webp', 'Uganda Tourism Board'),
]


@require_POST
def set_currency(request):
    """Remember the visitor's choice of USD or UGX and send them back."""
    nxt = request.POST.get('next') or '/'
    if not url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        nxt = '/'
    response = redirect(nxt)
    chosen = request.POST.get('currency')
    if chosen in money.Currency.values:
        response.set_cookie(money.COOKIE, chosen, max_age=365 * 24 * 3600, samesite='Lax',
                            secure=request.is_secure())
    return response


def home(request):
    tours = Itinerary.objects.published().prefetch_related('destinations')
    return render(request, 'main/home.html', {
        'destinations': Destination.objects.published(),
        'styles': TripStyle.objects.published(),
        'featured_tours': tours.filter(is_featured=True)[:6] or tours[:6],
        'departures': (
            Departure.objects.upcoming().with_seats().filter(itinerary__is_published=True)
            .select_related('itinerary')[:4]
        ),
        'places': Place.objects.published().filter(is_featured=True).select_related('destination')[:8],
        'reviews': Review.objects.filter(is_published=True)[:9],
        'posts': Post.objects.published().select_related('category')[:3],
        'partner_logos': PARTNER_LOGOS,
    })


def gallery(request):
    photos = Photo.objects.select_related('destination')
    return render(request, 'main/gallery.html', {
        'photos': photos,
        'videos': Video.objects.all(),
        'breadcrumbs': [('Gallery', None)],
    })


def error_404(request, exception):
    return render(request, '404.html', {'noindex': True}, status=404)


def error_500(request):
    # Rendered without context processors' database work so it can't fail itself.
    return render(request, '500.html', status=500)


@cache_control(max_age=86400)
def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /ckeditor/',
        'Disallow: /thank-you/',
        'Disallow: /tours/reservation/',
        'Disallow: /*/reserve/',
        '',
        f'Sitemap: {settings.SITE_URL}{reverse("sitemap")}',
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain')


@cache_control(max_age=86400)
def humans_txt(request):
    body = (
        '/* TEAM */\n'
        'Client: Kaizen Safaris\n'
        'Site: ' + settings.SITE_URL + '\n\n'
        'Developer: DakdotCreations Limited\n'
        'Site: https://dakdot.com\n'
        'Location: Uganda\n\n'
        '/* SITE */\n'
        'Standards: HTML5, CSS3\n'
        'Components: Django, Tailwind CSS, Alpine.js, GSAP\n'
    )
    return HttpResponse(body, content_type='text/plain; charset=utf-8')
