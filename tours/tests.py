import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from destinations.models import Destination
from tours.models import Day, Departure, Itinerary, Reservation

# 1x1 GIF, enough for ImageField.
PIXEL = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
         b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
MEDIA = tempfile.mkdtemp()


def image(name='x.gif'):
    return SimpleUploadedFile(name, PIXEL, content_type='image/gif')


def make_tour(**kwargs):
    dest = Destination.objects.first() or Destination.objects.create(name='Uganda', summary='s', cover=image())
    fields = {'name': 'Gorilla trek', 'summary': 's', 'cover': image(), 'duration_days': 3, 'price_from_usd': Decimal('1000')}
    fields.update(kwargs)
    tour = Itinerary.objects.create(**fields)
    tour.destinations.add(dest)
    return tour


@override_settings(MEDIA_ROOT=MEDIA)
class ModelTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.tour = make_tour()
        self.start = timezone.localdate() + timedelta(days=30)

    def test_slugs_are_unique(self):
        other = make_tour()
        self.assertEqual(self.tour.slug, 'gorilla-trek')
        self.assertEqual(other.slug, 'gorilla-trek-2')

    def test_end_date_from_duration(self):
        dep = Departure.objects.create(itinerary=self.tour, start_date=self.start)
        self.assertEqual(dep.end_date, self.start + timedelta(days=2))

    def test_seats_count_only_holding_reservations(self):
        dep = Departure.objects.create(itinerary=self.tour, start_date=self.start, seats_total=5)
        Reservation.objects.create(departure=dep, full_name='A', email='a@x.com', phone='1', travellers=2)
        Reservation.objects.create(departure=dep, full_name='B', email='b@x.com', phone='1', travellers=2,
                                   status=Reservation.Status.CANCELLED)
        self.assertEqual(dep.seats_left, 3)
        self.assertEqual(Departure.objects.with_seats().get(pk=dep.pk).seats_left, 3)

    def test_bookable_rules(self):
        dep = Departure.objects.create(itinerary=self.tour, start_date=self.start, seats_total=1)
        self.assertTrue(dep.is_bookable)
        dep.booking_deadline = timezone.localdate() - timedelta(days=1)
        self.assertFalse(dep.is_bookable)
        dep.booking_deadline = None
        dep.status = Departure.Status.CLOSED
        self.assertFalse(dep.is_bookable)
        dep.status = Departure.Status.OPEN
        dep.start_date = timezone.localdate()
        self.assertFalse(dep.is_bookable)

    def test_reservation_reference_and_amount(self):
        dep = Departure.objects.create(itinerary=self.tour, start_date=self.start, price_usd=Decimal('900'))
        res = Reservation.objects.create(departure=dep, full_name='A', email='a@x.com', phone='1', travellers=3)
        self.assertRegex(res.reference, r'^KZ-[A-Z2-9]{6}$')
        self.assertEqual(res.amount_due, Decimal('2700'))
        self.assertEqual(res.balance, Decimal('2700'))

    def test_day_label(self):
        self.assertEqual(Day(day_from=2).label, 'Day 2')
        self.assertEqual(Day(day_from=2, day_to=4).label, 'Days 2–4')

    def test_flexible_duration_label(self):
        flex = make_tour(format=Itinerary.Format.FLEXIBLE, duration_days=None, duration_note='')
        self.assertEqual(flex.duration_label, 'Flexible length')
        self.assertEqual(self.tour.duration_label, '3 days')

    def test_inclusions_list(self):
        self.tour.inclusions = '- Permit\n\n• Lodge\nGuide '
        self.assertEqual(self.tour.inclusions_list, ['Permit', 'Lodge', 'Guide'])


@override_settings(MEDIA_ROOT=MEDIA)
class ReservationFlowTests(TestCase):
    def setUp(self):
        self.tour = make_tour()
        self.dep = Departure.objects.create(
            itinerary=self.tour, start_date=timezone.localdate() + timedelta(days=30), seats_total=3,
        )
        self.url = reverse('tours:reserve', kwargs={'slug': self.tour.slug, 'pk': self.dep.pk})

    def post(self, **overrides):
        data = {'full_name': 'Ann', 'email': 'ann@example.com', 'phone': '+256700000000', 'country': 'UG',
                'travellers': 2, 'message': '', 'agree': 'on', 'website': ''}
        data.update(overrides)
        return self.client.post(self.url, data)

    def test_reserve_creates_reservation_and_shows_confirmation(self):
        response = self.post()
        res = Reservation.objects.get()
        self.assertRedirects(response, reverse('tours:reserved', kwargs={'reference': res.reference}))
        page = self.client.get(response['Location'])
        self.assertContains(page, res.reference)

    def test_cannot_exceed_seats(self):
        response = self.post(travellers=4)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only 3 seats left')
        self.assertFalse(Reservation.objects.exists())

    def test_honeypot_blocks_bots(self):
        self.post(website='http://spam.example')
        self.assertFalse(Reservation.objects.exists())

    def test_confirmation_page_is_private(self):
        self.post()
        ref = Reservation.objects.get().reference
        self.client.logout()
        self.client.cookies.clear()
        self.assertEqual(self.client.get(reverse('tours:reserved', kwargs={'reference': ref})).status_code, 404)

    def test_full_departure_redirects_to_tour(self):
        Reservation.objects.create(departure=self.dep, full_name='X', email='x@x.com', phone='1', travellers=3)
        response = self.client.get(self.url)
        self.assertRedirects(response, self.tour.get_absolute_url())
