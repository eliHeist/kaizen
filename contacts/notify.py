"""Email notifications. Failures are logged, never shown to visitors: the
submission itself is already saved in the database."""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from contacts.models import Recipient
from main.models import SiteSettings

logger = logging.getLogger(__name__)


def staff_emails():
    emails = list(Recipient.objects.filter(is_active=True).values_list('email', flat=True))
    return emails or [SiteSettings.load().email]


def send(subject, template, context, to, reply_to=None):
    context = {'site': SiteSettings.load(), 'SITE_URL': settings.SITE_URL, **context}
    html = render_to_string(template, context)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        reply_to=[reply_to] if reply_to else None,
    )
    msg.attach_alternative(html, 'text/html')
    try:
        msg.send()
        return True
    except Exception:  # SMTP errors come in many shapes
        logger.exception('Could not send "%s" to %s', subject, to)
        return False


def enquiry_received(enquiry):
    subject = f'{enquiry.get_kind_display()}: {enquiry.name}'
    if enquiry.itinerary:
        subject += f' ({enquiry.itinerary.name})'
    details = [
        (key.replace('_', ' ').capitalize(), ', '.join(value) if isinstance(value, list) else value)
        for key, value in enquiry.details.items()
    ]
    send(subject, 'emails/enquiry_staff.html', {'enquiry': enquiry, 'details': details}, staff_emails(),
         reply_to=enquiry.email)


def reservation_received(reservation):
    dep = reservation.departure
    send(
        f'New reservation {reservation.reference}: {dep.itinerary.name} ({dep.start_date:%d %b %Y})',
        'emails/reservation_staff.html', {'reservation': reservation}, staff_emails(), reply_to=reservation.email,
    )
    send(
        f'Your Kaizen Safaris reservation {reservation.reference}',
        'emails/reservation_traveller.html', {'reservation': reservation}, [reservation.email],
    )
