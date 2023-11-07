from django.conf import settings
from django.http import BadHeaderError, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.core.mail import send_mail

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
        
        try:
            message = f'''
                Name: {name}
                Email: {email}
                Phone: {phone}
                Itinerary: {itinerary.name}
                Link: kaizensafaris.com{reverse_lazy('destinations:itinerary-detail', kwargs={"pk": itinerary.pk})}
            '''
            subject = f'Quotation for {itinerary.name}'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [r.email for r in Receipient.objects.all()], fail_silently=False)
            # print(message)
        except BadHeaderError:
            return HttpResponse('Invalid header found. ')
        context = {
            'itinerary': itinerary,
        }
        return render(request, template_name, context)
