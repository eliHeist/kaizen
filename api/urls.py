from django.urls import path

from api.views import apiDestinations, apiOverview, days

app_name = 'api'

urlpatterns = [
    path('', apiOverview, name='overview'),
    path('destinations/<str:pk>', apiDestinations, name='destinations'),
    path('days/<str:pk>', days, name='days'),
]