from django.db import models
from ckeditor.fields import RichTextField

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
    price = models.PositiveIntegerField(null=True, blank=True)
    is_upcoming = models.BooleanField(default=False)
    details = RichTextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Itinerary'
        verbose_name_plural = 'Itineraries'

    def __str__(self):
        return self.name
    
    def Duration(self):
        if self.return_date and self.departure_date:
            difference = str(self.return_date - self.departure_date)[:-9]
            dayz = difference.split(' ')[0]
            # include the last day
            days = int(dayz) + 1
            return days
        else:
            return 0


class Day(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    image = models.ImageField(null=True, blank=True)
    day = models.CharField(max_length=6, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    tourist_attraction = models.CharField(max_length=100, null=True, blank=True)
    best_buy = models.CharField(max_length=50, null=True, blank=True)
    food_speciality = models.CharField(max_length=50, null=True, blank=True)
    activity = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Day'
        verbose_name_plural = 'Days'

    def __str__(self):
        return self.title
