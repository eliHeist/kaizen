from email.policy import default
from pyexpat import model
from django.db import models

# Create your models here.
class Destination(models.Model):
    name = models.CharField(max_length=20)
    video = models.FileField(null=True)
    image = models.ImageField(null=True)

    def __str__(self):
        return self.name


class Itinerary(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='itineraries')
    departure_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    is_upcoming = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Itinerary'
        verbose_name_plural = 'Itineraries'

    def __str__(self):
        return self.name
    
    def Duration(self):
        return str(self.return_date - self.departure_date)[:-9]


class Day(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    image = models.ImageField(null=True)
    day = models.CharField(max_length=6, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    tourist_attraction = models.CharField(max_length=100)
    best_buy = models.CharField(max_length=50)
    food_speciality = models.CharField(max_length=50)
    activity = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Day'
        verbose_name_plural = 'Days'

    def __str__(self):
        return self.title
