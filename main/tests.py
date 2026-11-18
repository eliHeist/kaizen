import json
import re
import shutil
import tempfile
from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from blog.models import Author, Category, Post, Tag
from contacts.models import Enquiry, Recipient
from destinations.models import Destination, Place, PlaceImage, TripStyle
from main.models import Photo, Review, Video
from rentals.models import RentalCategory, RentalItem
from tours.models import Day, Departure, Itinerary
from tours.tests import image

MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA, SITE_URL='https://kaizen-safaris.com')
class PageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dest = Destination.objects.create(name='Uganda', summary='Pearl of Africa', cover=image())
        cls.style = TripStyle.objects.create(name='Honeymoon', summary='Romance')
        cls.place = Place.objects.create(destination=cls.dest, name='Lake Bunyonyi', summary='Lake', cover=image())
        cls.place.styles.add(cls.style)
        PlaceImage.objects.create(place=cls.place, image=image())
        cls.tour = Itinerary.objects.create(name='Gorilla trek', summary='Gorillas', cover=image(), duration_days=3,
                                            price_from=1000, inclusions='Permit', exclusions='Flights')
        cls.tour.destinations.add(cls.dest)
        cls.tour.styles.add(cls.style)
        Day.objects.create(itinerary=cls.tour, day_from=1, title='Arrive', breakfast=True)
        cls.flex = Itinerary.objects.create(name='Flexible honeymoon', summary='Your way', cover=image(),
                                            format=Itinerary.Format.FLEXIBLE)
        cls.flex.destinations.add(cls.dest)
        cls.flex.places.add(cls.place)
        cls.dep = Departure.objects.create(itinerary=cls.tour, start_date=timezone.localdate() + timedelta(days=20))
        Review.objects.create(name='Ann', text='Great', itinerary=cls.tour)
        Photo.objects.create(image=image())
        Video.objects.create(title='Trailer', url='https://youtu.be/aqz-KE-bpKQ')
        cat = RentalCategory.objects.create(name='Cars')
        cls.car = RentalItem.objects.create(category=cat, name='Land Cruiser', image=image(), price=150)
        author = Author.objects.create(name='Grace')
        cls.category = Category.objects.create(name='Tips')
        cls.tag = Tag.objects.create(name='Gorillas')
        cls.post = Post.objects.create(title='Packing list', excerpt='What to bring', body='<p>Boots</p>', cover=image(),
                                       status=Post.Status.PUBLISHED, author=author, category=cls.category)
        cls.post.tags.add(cls.tag)
        cls.post.itineraries.add(cls.tour)
        Recipient.objects.create(email='staff@example.com')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def urls(self):
        return [
            reverse('main:home'),
            reverse('main:gallery'),
            reverse('destinations:list'),
            self.dest.get_absolute_url(),
            self.place.get_absolute_url(),
            reverse('tours:list'),
            reverse('tours:list') + '?destination=uganda&style=honeymoon&format=flexible&scheduled=1&q=honey&sort=price',
            reverse('tours:departures'),
            self.style.get_absolute_url(),
            self.tour.get_absolute_url(),
            self.flex.get_absolute_url(),
            self.dep.get_reserve_url(),
            reverse('rentals:list'),
            reverse('blog:list'),
            reverse('blog:list') + '?q=pack',
            self.post.get_absolute_url(),
            self.category.get_absolute_url(),
            self.tag.get_absolute_url(),
            self.post.author.get_absolute_url(),
            reverse('contacts:contact'),
            reverse('contacts:plan'),
            reverse('contacts:thanks'),
        ]

    def test_pages_render(self):
        for url in self.urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<link rel="canonical"')

    def test_structured_data_is_valid_json(self):
        for url in (reverse('main:home'), self.tour.get_absolute_url(), self.post.get_absolute_url(),
                    self.place.get_absolute_url(), self.dest.get_absolute_url()):
            html = self.client.get(url).content.decode()
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
            self.assertTrue(blocks, url)
            for block in blocks:
                json.loads(block)

    def test_developer_credit_is_hidden_not_visible(self):
        html = self.client.get(reverse('main:home')).content.decode()
        self.assertIn('DakdotCreations', html)
        body = html.split('<body', 1)[1]
        visible = re.sub(r'<script.*?</script>', '', body, flags=re.S)
        self.assertNotIn('Dakdot', visible)

    def test_unpublished_content_404s(self):
        Itinerary.objects.filter(pk=self.tour.pk).update(is_published=False)
        self.assertEqual(self.client.get(self.tour.get_absolute_url()).status_code, 404)

    def test_filtered_listing_is_noindex(self):
        response = self.client.get(reverse('tours:list') + '?style=honeymoon')
        self.assertContains(response, 'noindex')
        self.assertNotContains(self.client.get(reverse('tours:list')), 'noindex')

    def test_quote_form_saves_enquiry_and_emails_staff(self):
        response = self.client.post(self.tour.get_absolute_url(), {
            'name': 'Ann', 'email': 'ann@example.com', 'phone': '', 'travellers': 2, 'travel_date': '', 'message': 'Hi',
        })
        self.assertEqual(response.status_code, 302)
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.kind, Enquiry.Kind.QUOTE)
        self.assertEqual(enquiry.itinerary, self.tour)
        self.assertEqual(mail.outbox[0].to, ['staff@example.com'])
        self.assertEqual(mail.outbox[0].reply_to, ['ann@example.com'])

    def test_plan_form_stores_extra_answers(self):
        self.client.post(reverse('contacts:plan'), {
            'name': 'Ann', 'email': 'ann@example.com', 'travellers': 2, 'destinations': [self.dest.pk],
            'styles': [self.style.pk], 'budget': 'unsure', 'days': 9,
        })
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.details['destinations'], ['Uganda'])
        self.assertEqual(enquiry.details['days'], 9)

    def test_rental_form_validates_dates(self):
        response = self.client.post(reverse('rentals:list'), {
            'name': 'Ann', 'email': 'ann@example.com', 'items': [self.car.pk],
            'travel_date': '2030-01-10', 'return_date': '2030-01-05',
        })
        self.assertContains(response, 'after the pick-up date')
        self.assertFalse(Enquiry.objects.exists())

    def test_contact_form(self):
        self.client.post(reverse('contacts:contact'), {'name': 'Ann', 'email': 'ann@example.com', 'message': 'Hello'})
        self.assertEqual(Enquiry.objects.get().kind, Enquiry.Kind.GENERAL)

    def test_sitemap_robots_humans(self):
        sitemap = self.client.get('/sitemap.xml').content.decode()
        for obj in (self.tour, self.place, self.dest, self.post, self.style):
            self.assertIn('https://kaizen-safaris.com' + obj.get_absolute_url(), sitemap)
        robots = self.client.get('/robots.txt').content.decode()
        self.assertIn('Sitemap: https://kaizen-safaris.com/sitemap.xml', robots)
        self.assertIn('DakdotCreations', self.client.get('/humans.txt').content.decode())

    @override_settings(DEBUG=False)
    def test_custom_404(self):
        response = self.client.get('/no-such-page/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Lost in the bush', status_code=404)
