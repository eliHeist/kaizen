from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.serializers import DaySerializer, DestinationSerializer

from destinations.models import Day, Destination


# Create your views here.
@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'booking': '/api/book/',
        'destinations': '/api/destinations/<str:pk>',
        'days': '/api/days/<pk>',
    }
    return Response(api_urls)

@api_view(['GET'])
def apiDestinations(request, pk):
    if pk == 'all':
        destinations = Destination.objects.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def days(request, pk):
    if pk == 'all':
        days = Day.objects.all()
        serializer = DaySerializer(days, many=True)
        return Response(serializer.data)