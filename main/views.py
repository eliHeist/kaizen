from datetime import datetime
from django.http import BadHeaderError, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from destinations.models import Destination, Itinerary
from main.models import EquipmentType, HoneymoonSpot, Photo, Review, TopSpot, YTVideo
from contacts.models import Receipient
import logging

def server_error500(request):
    logger = logging.getLogger(__name__)
    logger.error('Internal Server Error (500)')
    # Add any additional logging or handling here
    return render(request, '500.html', status=500)

def error404View(request, exception):
    return render(request, '404.html')
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
        host = request.get_host()
        current_datetime = datetime.now()
        current_datetime_string = current_datetime.strftime("%A, %d %B %Y  -  %I:%M %p")
        
        obj = {
            'honeymoon': honeymoon,
            'name': name,
            'email': email,
            'phone': phone,
            'host': host,
            'date': current_datetime_string,
            "link": f"{host}{reverse_lazy('main:honeymoon-detail', kwargs={'pk': honeymoon.pk})}"
        }
        
        try:
            email_html_message = render_to_string('emails/honeymoonemail_template.html', obj)
            email_plain_message = strip_tags(email_html_message)
            subject = f'Quotation for {honeymoon.name}'
            print(subject)
            
            send_mail(
                subject, 
                email_plain_message, 
                settings.EMAIL_HOST_USER, 
                [r.email for r in Receipient.objects.all()], 
                fail_silently=False,
                html_message=email_html_message,
            )
            
            print('Sent')
            # print(message)
        except Exception as ex:
            return HttpResponse(f'Error: {ex}')
        
        context = {
            'message': "honeymoon",
            'spot': honeymoon
        }
        return render(request, template_name, context)