from django.shortcuts import render
from django.views.generic import TemplateView

from destinations.models import Destination, Itinerary
from main.models import EquipmentType, Photo, Review, TopSpot, YTVideo

# Create your views here.

class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_tours'] = Itinerary.objects.filter(is_upcoming=True)
        context['topspots'] = TopSpot.objects.all().filter(feature=True)
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
