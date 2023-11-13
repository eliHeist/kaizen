from datetime import datetime
from django.conf import settings
from django.http import BadHeaderError, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from contacts.models import Receipient

from destinations.models import Destination, Itinerary

# Create your views here.
def destinationDetailView(request, pk):
    template_name = 'destinations/destination-detail.html'
    destination = Destination.objects.get(id=pk)
    itineraries = Itinerary.objects.filter(destination=destination)
    context = {
        "destination": destination,
        "itineraries": itineraries
    }
    return render(request, template_name, context)

def itineraryListView(request, pk):
    template_name = 'destinations/itinerary-list.html'
    destination = Destination.objects.get(id=pk)
    itineraries = Itinerary.objects.filter(destination=destination)
    context = {
        "itineraries": itineraries
    }
    return render(request, template_name, context)

class ItineraryDetailView(View):
    def get(self, request, pk):
        template_name = 'destinations/itinerary-detail.html'
        itinerary = Itinerary.objects.get(id=pk)
        context = {
            'itinerary': itinerary,
        }
        return render(request, template_name, context)
    
    def post(self, request, pk):
        template_name = 'main/honeymoons/success.html'
        itinerary = Itinerary.objects.get(id=pk)
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        host = request.get_host()
        current_datetime = datetime.now()
        current_datetime_string = current_datetime.strftime("%A, %d %B %Y  -  %I:%M %p")
        
        obj = {
            'itinerary': itinerary,
            'name': name,
            'email': email,
            'phone': phone,
            'host': host,
            'date': current_datetime_string,
            "link": f"{host}{reverse_lazy('destinations:itinerary-detail', kwargs={'pk': itinerary.pk})}"
        }
        
        try:
            email_html_message = render_to_string('emails/itineraryemail_template.html', obj)
            email_plain_message = strip_tags(email_html_message)
            subject = f'Quotation for {itinerary.name}'
            
            send_mail(
                subject, 
                email_plain_message, 
                settings.EMAIL_HOST_USER, 
                [r.email for r in Receipient.objects.all()], 
                fail_silently=False,
                html_message=email_html_message,
            )
            # print(message)
        except Exception as ex:
            return HttpResponse(f'Error: {ex}')
        context = {
            'itinerary': itinerary,
        }
        return render(request, template_name, context)
