from django.urls import path

from destinations.views import destinationDetailView, itineraryDetailView, itineraryListView

app_name = 'destinations'

urlpatterns = [
    path('<int:pk>/', destinationDetailView, name='destination-detail'),
    path('<int:pk>/itineraries/', itineraryListView, name='itinerary-list'),
    path('itineraries/<int:pk>', itineraryDetailView, name='itinerary-detail'),
]