from datetime import date

from django import forms
from django.db.models import Model

from contacts.models import Enquiry
from destinations.models import Destination, TripStyle
from rentals.models import RentalItem


class HoneypotMixin(forms.Form):
    """A field hidden from people with CSS. Bots that fill it in are rejected."""
    website = forms.CharField(required=False, label='Leave this empty', widget=forms.TextInput(attrs={'autocomplete': 'off', 'tabindex': '-1'}))

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam check failed.')
        return ''


class EnquiryForm(HoneypotMixin):
    """Base for forms stored as an Enquiry. Extra fields end up in ``details``."""
    kind = Enquiry.Kind.GENERAL
    core_fields = ('name', 'email', 'phone', 'message', 'travel_date', 'travellers')

    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'autocomplete': 'name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    phone = forms.CharField(
        max_length=40, required=False, label='Phone / WhatsApp',
        widget=forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
    )

    def save(self, request=None, itinerary=None):
        data = self.cleaned_data
        details = {}
        for key, value in data.items():
            if key in self.core_fields or key == 'website' or value in (None, '', [], ()):
                continue
            details[key] = _plain(value)
        return Enquiry.objects.create(
            kind=self.kind,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            message=data.get('message', ''),
            travel_date=data.get('travel_date'),
            travellers=data.get('travellers'),
            itinerary=itinerary,
            details=details,
            page_url=request.build_absolute_uri() if request else '',
        )


def _plain(value):
    """Turn form values into something JSON can store and people can read."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Model):
        return str(value)
    if hasattr(value, '__iter__') and not isinstance(value, str):
        return [str(v) for v in value]
    return value


DATE_INPUT = forms.DateInput(attrs={'type': 'date'})


class ContactForm(EnquiryForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label='How can we help?')


class QuoteForm(EnquiryForm):
    kind = Enquiry.Kind.QUOTE
    travel_date = forms.DateField(required=False, widget=DATE_INPUT, label='Preferred start date')
    travellers = forms.IntegerField(min_value=1, max_value=99, initial=2, label='Travellers')
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Anything we should know?')


class TripPlanForm(EnquiryForm):
    kind = Enquiry.Kind.TRIP_PLAN

    BUDGETS = [
        ('', 'Select a budget'),
        ('under-1500', 'Under US$1,500 per person'),
        ('1500-3000', 'US$1,500–3,000 per person'),
        ('3000-6000', 'US$3,000–6,000 per person'),
        ('6000+', 'Over US$6,000 per person'),
        ('unsure', 'Not sure yet'),
    ]

    country = forms.CharField(max_length=80, required=False, label='Country of residence')
    destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.none(), required=False, widget=forms.CheckboxSelectMultiple,
        label='Where would you like to go?',
    )
    styles = forms.ModelMultipleChoiceField(
        queryset=TripStyle.objects.none(), required=False, widget=forms.CheckboxSelectMultiple,
        label='What interests you?',
    )
    travel_date = forms.DateField(required=False, widget=DATE_INPUT, label='Approximate start date')
    days = forms.IntegerField(min_value=1, max_value=60, required=False, label='Number of days')
    travellers = forms.IntegerField(min_value=1, max_value=99, initial=2, label='Adults')
    children = forms.IntegerField(min_value=0, max_value=20, required=False, label='Children')
    budget = forms.ChoiceField(choices=BUDGETS, required=False)
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}), label='Tell us about your dream trip')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destinations'].queryset = Destination.objects.published()
        self.fields['styles'].queryset = TripStyle.objects.published()


class RentalForm(EnquiryForm):
    kind = Enquiry.Kind.RENTAL
    items = forms.ModelMultipleChoiceField(
        queryset=RentalItem.objects.none(), widget=forms.CheckboxSelectMultiple, label='What would you like to hire?',
    )
    travel_date = forms.DateField(widget=DATE_INPUT, label='Pick-up date')
    return_date = forms.DateField(widget=DATE_INPUT, label='Return date')
    with_driver = forms.BooleanField(required=False, label='I need a driver/guide')
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Anything else?')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['items'].queryset = RentalItem.objects.filter(is_available=True).select_related('category')

    def clean(self):
        data = super().clean()
        start, end = data.get('travel_date'), data.get('return_date')
        if start and end and end < start:
            self.add_error('return_date', 'The return date must be after the pick-up date.')
        return data
