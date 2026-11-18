from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from destinations.models import Destination, Place
from main import seo
from tours.models import Itinerary


def destination_list(request):
    destinations = Destination.objects.published()
    return render(request, 'destinations/destination_list.html', {
        'destinations': destinations,
        'breadcrumbs': [('Destinations', None)],
    })


def destination_detail(request, slug):
    destination = get_object_or_404(Destination.objects.published(), slug=slug)
    places = destination.places.published()
    tours = (
        Itinerary.objects.published().filter(destinations=destination)
        .prefetch_related('destinations').distinct()
    )
    posts = destination.posts.published()[:3]
    return render(request, 'destinations/destination_detail.html', {
        'destination': destination,
        'places': places,
        'tours': tours,
        'posts': posts,
        'jsonld': seo.destination(destination),
        'breadcrumbs': [('Destinations', reverse('destinations:list')), (destination.name, None)],
    })


def place_detail(request, destination, slug):
    place = get_object_or_404(
        Place.objects.published().select_related('destination'),
        destination__slug=destination, destination__is_published=True, slug=slug,
    )
    tours = place.itineraries.published().prefetch_related('destinations')
    nearby = place.destination.places.published().exclude(pk=place.pk)[:3]
    return render(request, 'destinations/place_detail.html', {
        'place': place,
        'images': place.images.all(),
        'tours': tours,
        'nearby': nearby,
        'posts': place.posts.published()[:3],
        'jsonld': seo.place(place),
        'breadcrumbs': [
            ('Destinations', reverse('destinations:list')),
            (place.destination.name, place.destination.get_absolute_url()),
            (place.name, None),
        ],
    })
