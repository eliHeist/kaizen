from django.db import models

# Create your models here.
class Receipient(models.Model):
    email = models.EmailField()

    class Meta:
        verbose_name = 'Receipient'
        verbose_name_plural = 'Email Receipients'

    def __str__(self):
        return self.email