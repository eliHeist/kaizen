from django.http import BadHeaderError, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views import View
from django.conf import settings
from django.core.mail import send_mail

from destinations.models import Destination, Itinerary
from main.models import EquipmentType, HoneymoonSpot, Photo, Review, TopSpot, YTVideo
from contacts.models import Receipient

# Create your views here.

class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_tours'] = Itinerary.objects.filter(is_upcoming=True)
        context['topspots'] = TopSpot.objects.all().filter(feature=True)
        context['honeymoonspots'] = HoneymoonSpot.objects.all()
        context['tours'] = Itinerary.objects.all().filter(is_upcoming=False)
        context['reviews'] = Review.objects.all()
        return context
    

def bookingView(request):
    template_name = 'main/booking.html'
    context = {}
    return render(request, template_name, context)

def equipmentView(request):
    template_name = 'main/equipment.html'
    types = EquipmentType.objects.all()
    context = {
        "types": types
    }
    return render(request, template_name, context)

def galleryView(request):
    template_name = 'main/gallery.html'
    photos = Photo.objects.all()
    videos = YTVideo.objects.all()
    context = {
        "photos": photos,
        "videos": videos,
    }
    return render(request, template_name, context)

def error404View(request, exception):
    return render(request, '404.html')

class HoneymoonView(View):
    def get(self, request, pk, **kwargs):
        honeymoon = HoneymoonSpot.objects.get(pk=pk)
        template_name = 'main/honeymoons/detail.html'
        context = {
            'spot': honeymoon
        }
        return render(request, template_name, context)
    
    def post(self, request, pk):
        print('hmoon post')
        honeymoon = HoneymoonSpot.objects.get(pk=pk)
        template_name = 'main/honeymoons/success.html'
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        print('gotten')
        
        try:
            message = f'''
                Name: {name}
                Email: {email}
                Phone: {phone}
                Spot: {honeymoon.name}
                Link: kaizensafaris.com{reverse_lazy('main:honeymoon-detail', kwargs={"pk": honeymoon.pk})}
            '''
            print(message)
            subject = f'Quotation for {honeymoon.name}'
            print(subject)
            send_mail(subject, message, settings.EMAIL_HOST_USER, [r.email for r in Receipient.objects.all()], fail_silently=False)
            print('Sent')
            # print(message)
        except BadHeaderError:
            return HttpResponse('Invalid header found. ')
        
        context = {
            'message': "honeymoon",
            'spot': honeymoon
        }
        return render(request, template_name, context)