from django.shortcuts import redirect, render
from django.urls import reverse

from contacts import notify
from contacts.forms import ContactForm, TripPlanForm
from tours.models import Itinerary


def _handle(request, form_class, template, extra=None):
    form = form_class(request.POST or None, initial=request.GET.dict() if request.method == 'GET' else None)
    if request.method == 'POST' and form.is_valid():
        enquiry = form.save(request)
        notify.enquiry_received(enquiry)
        return redirect('contacts:thanks')
    return render(request, template, {'form': form, **(extra or {})})


def contact(request):
    return _handle(request, ContactForm, 'contacts/contact.html', {'breadcrumbs': [('Contact us', None)]})


def plan_trip(request):
    return _handle(request, TripPlanForm, 'contacts/plan_trip.html', {'breadcrumbs': [('Plan your trip', None)]})


def thanks(request):
    tour = Itinerary.objects.published().filter(slug=request.GET.get('for')).first()
    return render(request, 'contacts/thanks.html', {
        'tour': tour,
        'noindex': True,
        'breadcrumbs': [('Thank you', None)],
        'back_url': tour.get_absolute_url() if tour else reverse('main:home'),
    })
