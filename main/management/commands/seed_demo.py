"""Fill an empty development database with realistic sample content.

    uv run python manage.py seed_demo          # only runs when DEBUG=True
    uv run python manage.py seed_demo --flush  # wipe content tables first
"""
from datetime import timedelta
from decimal import Decimal
from itertools import cycle
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from blog.models import Author, Category, Post, Tag
from destinations.models import Destination, Place, PlaceImage, TripStyle
from main.models import Photo, Review, SiteSettings, Video
from rentals.models import RentalCategory, RentalItem
from tours.models import Day, Departure, Itinerary, Reservation

STATIC = Path(settings.BASE_DIR) / 'static' / 'public'
IMAGES = [
    STATIC / 'img' / name for name in (
        'lion.webp', 'elephants.webp', 'rinho.webp', 'crestedcrane.webp', 'lionafrica.webp', 'booking.webp',
    )
] + sorted((STATIC / 'images').glob('*.jpeg'))

LOREM = (
    '<p>Expect early starts, long golden evenings and guides who know every track by heart. '
    'We plan around the seasons and the wildlife, so every day has room for the unexpected: a leopard in a fig tree, '
    'a breeding herd crossing the road, or a sundowner nobody wants to end.</p>'
    '<h2>Good to know</h2><ul><li>Private 4x4 safari vehicle with pop-up roof</li>'
    '<li>English-speaking driver-guide throughout</li><li>Flexible start dates all year</li></ul>'
)


def ugx(usd):
    """Demo UGX price: the USD price at roughly 3,700 shillings, rounded to 5,000."""
    return Decimal(round(Decimal(usd) * 3700 / 5000) * 5000)


class Command(BaseCommand):
    help = 'Create sample destinations, tours, departures, posts and rentals for local development.'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing content first.')
        parser.add_argument('--force', action='store_true', help='Run even when DEBUG is False.')

    def handle(self, *args, flush=False, force=False, **options):
        if not settings.DEBUG and not force:
            raise CommandError('Refusing to seed demo content with DEBUG=False (use --force if you really mean it).')
        if Itinerary.objects.exists() and not flush:
            raise CommandError('Content already exists. Re-run with --flush to replace it.')
        self.images = cycle(IMAGES)
        with transaction.atomic():
            if flush:
                for model in (Reservation, Departure, Day, Post, Tag, Category, Author, Review, Photo, Video,
                              Itinerary, PlaceImage, Place, TripStyle, Destination, RentalItem, RentalCategory):
                    model.objects.all().delete()
            self.seed()
        self.stdout.write(self.style.SUCCESS('Demo content created.'))

    def img(self):
        path = next(self.images)
        return File(open(path, 'rb'), name=path.name)

    def make(self, model, image_field='cover', **fields):
        obj = model(**fields)
        with self.img() as f:
            getattr(obj, image_field).save(f.name, f, save=False)
        obj.save()
        return obj

    def seed(self):
        site = SiteSettings.load()
        site.payment_instructions = (
            '<p><strong>Deposit:</strong> 30% within 7 days of confirmation, balance 45 days before departure.</p>'
            '<p><strong>Mobile money:</strong> MTN 0755 312 238 (Kaizen Safaris)</p>'
            '<p><strong>Bank transfer:</strong> details are sent with your confirmation email.</p>'
        )
        site.save()

        # Trip styles
        styles = {}
        for i, (name, icon, summary) in enumerate([
            ('Gorilla trekking', 'fa-solid fa-paw', 'Hike into Bwindi and Volcanoes to spend an hour with a habituated mountain gorilla family.'),
            ('Wildlife safari', 'fa-solid fa-binoculars', 'Classic game drives for the Big Five across savannah, swamp and forest.'),
            ('Honeymoon', 'fa-solid fa-heart', 'Slow, romantic journeys with lakeside lodges, private dinners and time to yourselves.'),
            ('Birding', 'fa-solid fa-dove', 'More than 1,000 species, from the shoebill to the great blue turaco.'),
            ('Family', 'fa-solid fa-children', 'Shorter drives, kid-friendly lodges and guides who love curious questions.'),
            ('Adventure', 'fa-solid fa-person-hiking', 'White-water rafting on the Nile, crater hikes and mountain treks.'),
        ]):
            styles[name] = self.make(TripStyle, name=name, icon=icon, summary=summary, order=i, body=f'<p>{summary}</p>')

        # Destinations and places
        dest_data = [
            ('Uganda', 'The Pearl of Africa', 'Mountain gorillas, chimpanzees, the source of the Nile and ten national parks in a country the size of the UK.', 'June to September and December to February'),
            ('Kenya', 'Home of the great migration', 'The Maasai Mara, Amboseli under Kilimanjaro and white-sand Indian Ocean beaches.', 'July to October for the migration'),
            ('Tanzania', 'Serengeti, Ngorongoro and Zanzibar', 'Endless plains, the world’s largest intact caldera and spice-island beaches.', 'June to October; calving season January to March'),
            ('Rwanda', 'Land of a thousand hills', 'Gorilla and golden monkey treks in Volcanoes National Park and the calm shores of Lake Kivu.', 'June to September'),
        ]
        dests = {}
        for i, (name, tagline, summary, best) in enumerate(dest_data):
            dests[name] = self.make(Destination, name=name, tagline=tagline, summary=summary, best_time_to_visit=best,
                                    body=f'<p>{summary}</p>' + LOREM, order=i)

        place_data = [
            ('Uganda', 'Bwindi Impenetrable Forest', Place.Kind.PARK, 'Ancient rainforest sheltering almost half the world’s mountain gorillas.', ['Gorilla trekking'], True),
            ('Uganda', 'Murchison Falls', Place.Kind.WATER, 'The Nile forces itself through a 7-metre gorge before a river full of hippos and crocodiles.', ['Wildlife safari'], True),
            ('Uganda', 'Queen Elizabeth National Park', Place.Kind.PARK, 'Tree-climbing lions in Ishasha and a boat cruise on the Kazinga Channel.', ['Wildlife safari', 'Family'], True),
            ('Uganda', 'Lake Bunyonyi', Place.Kind.WATER, 'A terraced lake of 29 islands: canoes, cool mornings and the perfect honeymoon pause.', ['Honeymoon'], True),
            ('Uganda', 'Kibale Forest', Place.Kind.PARK, 'The primate capital of the world, with habituated chimpanzee families.', ['Birding'], False),
            ('Uganda', 'Jinja, Source of the Nile', Place.Kind.WATER, 'Grade-five rapids, bungee jumping and sunset cruises where the Nile begins.', ['Adventure'], False),
            ('Kenya', 'Maasai Mara', Place.Kind.PARK, 'Big cats all year and the river crossings of the great migration.', ['Wildlife safari'], True),
            ('Kenya', 'Diani Beach', Place.Kind.BEACH, 'Seventeen kilometres of white sand on the Indian Ocean.', ['Honeymoon'], False),
            ('Tanzania', 'Serengeti', Place.Kind.PARK, 'The classic endless plain, with predators following the herds.', ['Wildlife safari'], True),
            ('Tanzania', 'Zanzibar', Place.Kind.BEACH, 'Stone Town alleys, spice farms and turquoise lagoons.', ['Honeymoon'], True),
            ('Rwanda', 'Volcanoes National Park', Place.Kind.MOUNTAIN, 'Gorillas and golden monkeys in the bamboo of the Virunga volcanoes.', ['Gorilla trekking'], True),
        ]
        places = {}
        for i, (dest, name, kind, summary, style_names, featured) in enumerate(place_data):
            place = self.make(Place, destination=dests[dest], name=name, kind=kind, summary=summary,
                              body=f'<p>{summary}</p>' + LOREM, is_featured=featured, order=i)
            place.styles.set([styles[s] for s in style_names])
            for _ in range(3):
                self.make(PlaceImage, image_field='image', place=place, caption=f'{name}')
            places[name] = place

        # Itineraries
        today = timezone.localdate()
        gorilla = self.make(
            Itinerary, name='8-Day Uganda Gorillas, Chimps & Big Game Safari', format=Itinerary.Format.DAY_BY_DAY,
            summary='Track chimpanzees in Kibale, cruise the Kazinga Channel, find Ishasha’s tree-climbing lions and meet mountain gorillas in Bwindi.',
            overview=LOREM, duration_days=8, price_from_usd=Decimal('2850'), price_from_ugx=ugx('2850'), is_featured=True,
            inclusions='Gorilla permit (US$800)\nChimpanzee permit\nAll park fees\nFull-board accommodation\nPrivate 4x4 with driver-guide\nBottled water',
            exclusions='International flights\nUganda visa\nTips and gratuities\nTravel insurance',
        )
        gorilla.destinations.set([dests['Uganda']])
        gorilla.styles.set([styles['Gorilla trekking'], styles['Wildlife safari']])
        gorilla.places.set([places['Kibale Forest'], places['Queen Elizabeth National Park'], places['Bwindi Impenetrable Forest']])
        for d_from, d_to, title, place, lodge in [
            (1, None, 'Arrive in Entebbe', None, 'Karibu Entebbe Guesthouse'),
            (2, None, 'Drive to Kibale Forest', places['Kibale Forest'], 'Primate Lodge Kibale'),
            (3, None, 'Chimpanzee tracking and Bigodi swamp walk', places['Kibale Forest'], 'Primate Lodge Kibale'),
            (4, 5, 'Queen Elizabeth: game drives and Kazinga Channel cruise', places['Queen Elizabeth National Park'], 'Mweya Safari Lodge'),
            (6, None, 'Ishasha tree-climbing lions, on to Bwindi', places['Bwindi Impenetrable Forest'], 'Buhoma Lodge'),
            (7, None, 'Gorilla trekking in Bwindi', places['Bwindi Impenetrable Forest'], 'Buhoma Lodge'),
            (8, None, 'Return to Entebbe', None, ''),
        ]:
            day = Day(itinerary=gorilla, day_from=d_from, day_to=d_to, title=title, place=place, accommodation=lodge,
                      description=f'<p>{title}. ' + LOREM[3:], breakfast=d_from > 1, lunch=True, dinner=d_from < 8)
            with self.img() as f:
                day.image.save(f.name, f, save=False)
            day.save()

        honeymoon = self.make(
            Itinerary, name='Uganda Honeymoon: Gorillas & Lake Bunyonyi', format=Itinerary.Format.FLEXIBLE,
            summary='A slow, romantic journey you shape together: lakeside cottages, a private gorilla trek and as many lazy mornings as you like.',
            overview='<p>This is a flexible itinerary. Tell us how many nights you want in each place and we build the trip around you.</p>' + LOREM,
            duration_days=7, duration_note='6 to 10 days, you choose', price_from_usd=Decimal('3400'), price_from_ugx=ugx('3400'), is_featured=True,
            inclusions='Gorilla permits\nBoutique lodges with lake or forest views\nPrivate candle-lit dinner\nPrivate vehicle and guide',
            exclusions='Flights\nVisas\nDrinks at lodges',
        )
        honeymoon.destinations.set([dests['Uganda']])
        honeymoon.styles.set([styles['Honeymoon'], styles['Gorilla trekking']])
        honeymoon.places.set([places['Lake Bunyonyi'], places['Bwindi Impenetrable Forest']])

        mara = self.make(
            Itinerary, name='Maasai Mara Migration Group Safari', format=Itinerary.Format.DAY_BY_DAY,
            summary='Join a small group for four days of migration river crossings and big-cat sightings in the Mara.',
            overview=LOREM, duration_days=4, price_from_usd=Decimal('1290'), price_from_ugx=ugx('1290'), is_featured=True,
            inclusions='Shared 4x4 safari vehicle\nPark fees\nTented camp, full board',
            exclusions='Flights\nTips',
        )
        mara.destinations.set([dests['Kenya']])
        mara.styles.set([styles['Wildlife safari']])
        mara.places.set([places['Maasai Mara']])
        for n, title in enumerate(['Nairobi to the Mara', 'Full day in the Mara', 'Mara River crossings', 'Return to Nairobi'], start=1):
            Day.objects.create(itinerary=mara, day_from=n, title=title, description=f'<p>{title}.</p>',
                               accommodation='' if n == 4 else 'Mara Tented Camp', breakfast=n > 1, lunch=True, dinner=n < 4)

        east = self.make(
            Itinerary, name='Tailor-made East Africa: Serengeti to Zanzibar', format=Itinerary.Format.FLEXIBLE,
            summary='Combine the Serengeti, Ngorongoro and the beaches of Zanzibar at your own pace.',
            overview=LOREM, duration_days=None, duration_note='10 to 14 days', price_from_usd=None,
            inclusions='Planning with a dedicated specialist\nAll ground transport\nPark fees',
            exclusions='International flights',
        )
        east.destinations.set([dests['Tanzania']])
        east.styles.set([styles['Wildlife safari'], styles['Honeymoon']])
        east.places.set([places['Serengeti'], places['Zanzibar']])

        rwanda = self.make(
            Itinerary, name='3-Day Rwanda Gorilla Express', format=Itinerary.Format.DAY_BY_DAY,
            summary='Fly into Kigali, trek gorillas in Volcanoes National Park and be home within the week.',
            overview=LOREM, duration_days=3, price_from_usd=Decimal('2390'), price_from_ugx=ugx('2390'),
        )
        rwanda.destinations.set([dests['Rwanda']])
        rwanda.styles.set([styles['Gorilla trekking']])
        rwanda.places.set([places['Volcanoes National Park']])
        for n, title in enumerate(['Kigali to Musanze', 'Gorilla trekking', 'Return to Kigali'], start=1):
            Day.objects.create(itinerary=rwanda, day_from=n, title=title, description=f'<p>{title}.</p>', lunch=True)

        # Scheduled departures and a few reservations
        dep1 = Departure.objects.create(itinerary=gorilla, start_date=today + timedelta(days=45), seats_total=8,
                                        status=Departure.Status.GUARANTEED, notes='Gorilla permits secured')
        Departure.objects.create(itinerary=gorilla, start_date=today + timedelta(days=120), seats_total=8)
        dep3 = Departure.objects.create(itinerary=mara, start_date=today + timedelta(days=60), seats_total=6,
                                        price_usd=Decimal('1190'), price_ugx=ugx('1190'), booking_deadline=today + timedelta(days=40))
        Departure.objects.create(itinerary=honeymoon, start_date=today + timedelta(days=90), seats_total=2, min_travellers=2)
        Reservation.objects.create(departure=dep1, full_name='Anna Schmidt', email='anna@example.com', phone='+49 151 000000',
                                   country='Germany', travellers=2, status=Reservation.Status.DEPOSIT, amount_paid=Decimal('1710'))
        Reservation.objects.create(departure=dep3, full_name='James Okello', email='james@example.com', phone='+256 700 000000',
                                   country='Uganda', travellers=5, status=Reservation.Status.CONFIRMED)

        # Reviews
        for name, country, text, tour in [
            ('Sarah & Tom', 'United Kingdom', 'Our gorilla trek was the most moving hour of our lives, and every detail around it was handled perfectly.', gorilla),
            ('Marco', 'Italy', 'Great guide, great lodges, and they changed our plans overnight when the rains came. Highly recommended.', gorilla),
            ('Aisha', 'Kenya', 'We saw three river crossings in two days. The group was small and the camp was beautiful.', mara),
            ('Lena', 'Netherlands', 'Lake Bunyonyi was the dreamiest end to our honeymoon. Thank you Kaizen!', honeymoon),
        ]:
            Review.objects.create(name=name, country=country, text=text, itinerary=tour, rating=5, source='SafariBookings')

        # Gallery
        for i in range(8):
            self.make(Photo, image_field='image', caption='', destination=dests['Uganda'], order=i)
        Video.objects.create(title='Kaizen Safaris on the road', url='https://www.youtube.com/watch?v=aqz-KE-bpKQ')

        # Rentals
        cars = RentalCategory.objects.create(name='Safari vehicles', icon='fa-solid fa-car-side',
                                             summary='Well-maintained 4x4s, self-drive or with a driver-guide.', order=0)
        camping = RentalCategory.objects.create(name='Camping gear', icon='fa-solid fa-campground',
                                                summary='Everything for a night under the stars.', order=1)
        for cat, name, cap, price, unit in [
            (cars, 'Toyota Land Cruiser (pop-up roof)', '7 seats, pop-up roof', '150', 'per day'),
            (cars, 'Toyota RAV4', '4 seats, ideal for self-drive', '60', 'per day'),
            (camping, 'Rooftop tent', 'Sleeps 2', '25', 'per night'),
            (camping, 'Dome tent and bedding set', 'Sleeps 3', '15', 'per night'),
            (camping, 'Camp kitchen box', 'Stove, cookware and cutlery for 4', '10', 'per day'),
        ]:
            self.make(RentalItem, image_field='image', category=cat, name=name, capacity=cap,
                      price_usd=Decimal(price), price_ugx=ugx(price), price_unit=unit, summary=f'{name}, cleaned and checked before every hire.')

        # Blog
        author = Author.objects.create(name='Grace Namata', role='Safari specialist',
                                       bio='Grace has guided travellers through Uganda’s parks for over ten years and still gets goosebumps at every gorilla encounter.')
        tips = Category.objects.create(name='Travel tips', description='Practical advice for planning your trip.', order=0)
        wildlife = Category.objects.create(name='Wildlife', description='Animals, birds and where to find them.', order=1)
        tag_g, tag_b, tag_p = (Tag.objects.create(name=n) for n in ('Gorillas', 'Budget', 'Packing'))
        for i, (title, cat, tags, tour, place, featured) in enumerate([
            ('How to get a gorilla permit in Uganda (and what it costs)', tips, [tag_g, tag_b], gorilla, places['Bwindi Impenetrable Forest'], True),
            ('What to pack for a gorilla trek', tips, [tag_g, tag_p], gorilla, places['Bwindi Impenetrable Forest'], False),
            ('Where to see tree-climbing lions', wildlife, [], gorilla, places['Queen Elizabeth National Park'], False),
            ('The best time to see the great migration', wildlife, [], mara, places['Maasai Mara'], False),
        ]):
            post = self.make(Post, title=title, category=cat, author=author, status=Post.Status.PUBLISHED,
                             published_at=timezone.now() - timedelta(days=7 * (i + 1)), is_featured=featured,
                             excerpt=f'{title}: everything we tell our own travellers before they go.',
                             body=('<p>Planning ahead makes all the difference.</p>' + LOREM) * 3)
            post.tags.set(tags)
            post.itineraries.set([tour])
            post.places.set([place])
            post.destinations.set([place.destination])
