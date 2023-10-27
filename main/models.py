from django.db import models

from destinations.models import Destination


# Create your models here.
class EquipmentType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)

    class Meta:
        verbose_name = 'Equipment Type'
        verbose_name_plural = ' Types of Equipments'

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(EquipmentType, on_delete=models.SET_NULL, related_name='equipments', blank=True, null=True)
    image = models.ImageField()
    price = models.CharField(max_length=10)
    description = models.TextField()

    class Meta:
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipments'

    def __str__(self):
        return self.name


class Photo(models.Model):
    image = models.ImageField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __str__(self):
        return 'Photo'


class YTVideo(models.Model):
    link = models.URLField()

    class Meta:
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'
    
    def __str__(self):
        return self.link


class Review(models.Model):
    reviewer = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.reviewer

class TopSpot(models.Model):
    image = models.ImageField()
    title = models.CharField(max_length=50)
    country = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    feature = models.BooleanField(default=False)

# class ReviewLink(models.Model):
#     link = models.URLField()
#     review = models.ForeignKey()