from django.db import models

from main.mixins import TimeStamped


class Recipient(models.Model):
    """Staff addresses that receive enquiry and reservation notifications."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'notification recipient'

    def __str__(self):
        return self.email


class Enquiry(TimeStamped):
    """Every form submission is stored here, so nothing is lost if email fails."""

    class Kind(models.TextChoices):
        GENERAL = 'general', 'General message'
        TRIP_PLAN = 'trip_plan', 'Tailor-made trip request'
        QUOTE = 'quote', 'Itinerary quote'
        RENTAL = 'rental', 'Rental enquiry'

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In progress'
        CLOSED = 'closed', 'Closed'

    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.GENERAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField(blank=True)
    itinerary = models.ForeignKey('tours.Itinerary', on_delete=models.SET_NULL, null=True, blank=True, related_name='enquiries')
    travel_date = models.DateField(null=True, blank=True)
    travellers = models.PositiveSmallIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True, help_text='Other answers from the form.')
    page_url = models.CharField(max_length=300, blank=True)
    staff_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'enquiries'

    def __str__(self):
        return f'{self.get_kind_display()} from {self.name}'
