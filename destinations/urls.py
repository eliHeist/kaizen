from django.urls import path

from destinations.views import destinationDetailView, ItineraryDetailView, itineraryListView

app_name = 'destinations'

urlpatterns = [
    path('<int:pk>/', destinationDetailView, name='detail'),
    path('<int:pk>/itineraries/', itineraryListView, name='itinerary-list'),
    path('itineraries/<int:pk>/', ItineraryDetailView.as_view(), name='itinerary-detail'),
]