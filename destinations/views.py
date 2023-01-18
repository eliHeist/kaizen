from django.shortcuts import render

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

def itineraryDetailView(request, pk):
    template_name = 'destinations/itinerary-detail.html'
    itinerary = Itinerary.objects.get(id=pk)
    context = {
        'itinerary': itinerary,
    }
    return render(request, template_name, context)
