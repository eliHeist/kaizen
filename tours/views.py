from urllib.parse import urlencode

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from contacts import notify
from contacts.forms import QuoteForm
from destinations.models import Destination, TripStyle
from main.models import Review
from tours.forms import ReservationForm
from tours.models import Departure, Itinerary, Reservation

SESSION_KEY = 'reservation_refs'


def _filtered_tours(params):
    tours = Itinerary.objects.published().prefetch_related('destinations', 'styles')
    if params.get('destination'):
        tours = tours.filter(destinations__slug=params['destination'])
    if params.get('style'):
        tours = tours.filter(styles__slug=params['style'])
    if params.get('format') in Itinerary.Format.values:
        tours = tours.filter(format=params['format'])
    if params.get('scheduled') == '1':
        tours = tours.filter(pk__in=Departure.objects.upcoming().values('itinerary'))
    q = (params.get('q') or '').strip()
    if q:
        tours = tours.filter(Q(name__icontains=q) | Q(summary__icontains=q) | Q(places__name__icontains=q))
    sort = params.get('sort')
    if sort == 'price':
        tours = tours.order_by('price_from', 'name')
    elif sort == 'duration':
        tours = tours.order_by('duration_days', 'name')
    return tours.distinct()


def tour_list(request):
    tours = _filtered_tours(request.GET)
    page = Paginator(tours, 12).get_page(request.GET.get('page'))
    active = {k: v for k, v in request.GET.items() if k != 'page' and v}
    return render(request, 'tours/tour_list.html', {
        'page': page,
        'tours': page.object_list,
        'destinations': Destination.objects.published(),
        'styles': TripStyle.objects.published(),
        'formats': Itinerary.Format.choices,
        'active': active,
        'querystring': urlencode(active),
        'breadcrumbs': [('Tours & safaris', None)],
    })


def style_detail(request, slug):
    style = get_object_or_404(TripStyle.objects.published(), slug=slug)
    return render(request, 'tours/style_detail.html', {
        'style': style,
        'tours': style.itineraries.published().prefetch_related('destinations'),
        'places': style.places.published().select_related('destination')[:6],
        'breadcrumbs': [('Tours & safaris', reverse('tours:list')), (style.name, None)],
    })


def departure_list(request):
    departures = (
        Departure.objects.upcoming().with_seats()
        .filter(itinerary__is_published=True)
        .select_related('itinerary').prefetch_related('itinerary__destinations')
    )
    return render(request, 'tours/departure_list.html', {
        'departures': departures,
        'breadcrumbs': [('Tours & safaris', reverse('tours:list')), ('Scheduled departures', None)],
    })


def tour_detail(request, slug):
    tour = get_object_or_404(
        Itinerary.objects.published().prefetch_related('destinations', 'styles', 'places__destination'),
        slug=slug,
    )
    form = QuoteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        enquiry = form.save(request, itinerary=tour)
        notify.enquiry_received(enquiry)
        messages.success(request, 'Thank you! We will send your quote within one working day.')
        return redirect(f"{reverse('contacts:thanks')}?for={tour.slug}")

    related = (
        Itinerary.objects.published().filter(destinations__in=tour.destinations.all())
        .exclude(pk=tour.pk).distinct().prefetch_related('destinations')[:3]
    )
    return render(request, 'tours/tour_detail.html', {
        'tour': tour,
        'days': tour.days.select_related('place') if tour.is_day_by_day else [],
        'departures': tour.departures.upcoming().with_seats(),
        'reviews': Review.objects.filter(is_published=True, itinerary=tour)[:6],
        'related': related,
        'posts': tour.posts.published()[:3],
        'form': form,
        'breadcrumbs': [('Tours & safaris', reverse('tours:list')), (tour.name, None)],
    })


def reserve(request, slug, pk):
    departure = get_object_or_404(
        Departure.objects.with_seats().select_related('itinerary'),
        pk=pk, itinerary__slug=slug, itinerary__is_published=True, is_published=True,
    )
    tour = departure.itinerary
    if not departure.is_bookable:
        messages.info(request, 'Sorry, this departure is no longer taking reservations. Ask us about other dates.')
        return redirect(tour.get_absolute_url())

    if request.method == 'POST':
        with transaction.atomic():
            # Lock the departure row so two people can't take the last seat at once.
            departure = Departure.objects.select_for_update().get(pk=departure.pk)
            form = ReservationForm(request.POST, departure=departure)
            if form.is_valid():
                reservation = form.save(commit=False)
                reservation.departure = departure
                reservation.save()
        if form.is_valid():
            notify.reservation_received(reservation)
            refs = request.session.get(SESSION_KEY, [])
            request.session[SESSION_KEY] = (refs + [reservation.reference])[-10:]
            return redirect('tours:reserved', reference=reservation.reference)
    else:
        form = ReservationForm(departure=departure)

    return render(request, 'tours/reserve.html', {
        'tour': tour,
        'departure': departure,
        'form': form,
        'breadcrumbs': [
            ('Tours & safaris', reverse('tours:list')),
            (tour.name, tour.get_absolute_url()),
            ('Reserve', None),
        ],
    })


def reserved(request, reference):
    # Only the browser that made the reservation can see its confirmation page.
    if reference not in request.session.get(SESSION_KEY, []):
        raise Http404
    reservation = get_object_or_404(Reservation.objects.select_related('departure__itinerary'), reference=reference)
    return render(request, 'tours/reserved.html', {'reservation': reservation, 'noindex': True})
