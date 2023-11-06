from django.urls import path

from main.views import HomeView, HoneymoonView, bookingView, equipmentView, galleryView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home-view'),
    path('equipment/', equipmentView, name='equipment-view'),
    path('gallery/', galleryView, name='gallery-view'),
    path('booking/', bookingView, name='booking-view'),
    path('honeymoon/<int:pk>/', HoneymoonView.as_view(), name='honeymoon-detail'),
]