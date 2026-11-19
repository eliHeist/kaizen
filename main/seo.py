"""schema.org structured data (JSON-LD) builders.

Templates render these with the ``jsonld`` filter from ``main.templatetags.kaizen``.
"""
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import strip_tags

from main.templatetags.kaizen import absolute

ORG_ID = '#organization'
DEVELOPER = {
    '@type': 'Organization',
    'name': 'DakdotCreations Limited',
    'url': 'https://dakdot.com',
}


def _url(path):
    return absolute(path)


def _image(fieldfile):
    return _url(fieldfile.url) if fieldfile else None


def organization(site):
    base = settings.SITE_URL
    address = {
        '@type': 'PostalAddress',
        'streetAddress': ', '.join(p for p in (site.address_line1, site.address_line2) if p),
        'addressLocality': site.city,
        'addressCountry': 'UG' if site.country.lower() == 'uganda' else site.country,
    }
    if site.po_box:
        address['postOfficeBoxNumber'] = site.po_box
    return {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'TravelAgency',
                '@id': base + '/' + ORG_ID,
                'name': site.site_name,
                'url': base + '/',
                'logo': _url(static('img/logo.webp')),
                'image': _url(static('img/lion.webp')),
                'description': site.description,
                'email': site.email,
                'telephone': site.phone_digits,
                'address': address,
                'areaServed': ['Uganda', 'Kenya', 'Tanzania', 'Rwanda'],
                'sameAs': [url for _, _, url in site.social_links],
            },
            {
                '@type': 'WebSite',
                '@id': base + '/#website',
                'url': base + '/',
                'name': site.site_name,
                'inLanguage': 'en',
                'publisher': {'@id': base + '/' + ORG_ID},
                'creator': DEVELOPER,
            },
        ],
    }


def _provider():
    return {'@id': settings.SITE_URL + '/' + ORG_ID}


def tour(itinerary, departures, days):
    data = {
        '@context': 'https://schema.org',
        '@type': 'TouristTrip',
        'name': itinerary.name,
        'description': itinerary.summary,
        'url': _url(itinerary.get_absolute_url()),
        'image': _image(itinerary.cover),
        'provider': _provider(),
        'touristType': [s.name for s in itinerary.styles.all()],
    }
    if days:
        data['itinerary'] = {
            '@type': 'ItemList',
            'numberOfItems': len(days),
            'itemListElement': [
                {
                    '@type': 'ListItem',
                    'position': i,
                    'item': {
                        '@type': 'TouristAttraction' if d.place else 'Thing',
                        'name': f'{d.label}: {d.title}',
                        **({'description': strip_tags(d.description)[:300]} if d.description else {}),
                    },
                }
                for i, d in enumerate(days, start=1)
            ],
        }
    elif itinerary.places.exists():
        data['itinerary'] = {
            '@type': 'ItemList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i, 'item': {'@type': 'TouristAttraction', 'name': p.name, 'url': _url(p.get_absolute_url())}}
                for i, p in enumerate(itinerary.places.all(), start=1)
            ],
        }
    offers = []
    for dep in departures:
        for currency, price in dep.effective_price.items():
            offers.append({
                '@type': 'Offer',
                'price': str(price),
                'priceCurrency': currency,
                'availability': 'https://schema.org/InStock' if dep.is_bookable else 'https://schema.org/SoldOut',
                'validThrough': (dep.booking_deadline or dep.start_date).isoformat(),
                'availabilityStarts': dep.start_date.isoformat(),
                'availabilityEnds': (dep.end_date or dep.start_date).isoformat(),
                'url': _url(dep.get_reserve_url()),
            })
    if not offers:
        for currency, price in itinerary.price_from.items():
            offers.append({
                '@type': 'Offer',
                'price': str(price),
                'priceCurrency': currency,
                'availability': 'https://schema.org/InStock',
                'url': _url(itinerary.get_absolute_url()),
            })
    if offers:
        data['offers'] = offers
    return data


def place(obj):
    return {
        '@context': 'https://schema.org',
        '@type': 'TouristAttraction',
        'name': obj.name,
        'description': obj.summary,
        'url': _url(obj.get_absolute_url()),
        'image': [_image(obj.cover)] + [_image(i.image) for i in obj.images.all()[:5]],
        'containedInPlace': {'@type': 'Country', 'name': obj.destination.name},
    }


def destination(obj):
    return {
        '@context': 'https://schema.org',
        '@type': 'TouristDestination',
        'name': obj.name,
        'description': obj.summary,
        'url': _url(obj.get_absolute_url()),
        'image': _image(obj.cover),
        'includesAttraction': [
            {'@type': 'TouristAttraction', 'name': p.name, 'url': _url(p.get_absolute_url())}
            for p in obj.places.published()
        ],
    }


def post(obj):
    data = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'headline': obj.title[:110],
        'description': obj.excerpt,
        'image': _image(obj.cover),
        'url': _url(obj.get_absolute_url()),
        'mainEntityOfPage': _url(obj.get_absolute_url()),
        'datePublished': obj.published_at.isoformat(),
        'dateModified': obj.updated_at.isoformat(),
        'publisher': _provider(),
        'wordCount': len(strip_tags(obj.body).split()),
    }
    if obj.author:
        data['author'] = {
            '@type': 'Person',
            'name': obj.author.name,
            'url': _url(obj.author.get_absolute_url()),
            **({'jobTitle': obj.author.role} if obj.author.role else {}),
        }
    if obj.category:
        data['articleSection'] = obj.category.name
    tags = [t.name for t in obj.tags.all()]
    if tags:
        data['keywords'] = ', '.join(tags)
    return data
