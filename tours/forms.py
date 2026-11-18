from django import forms

from contacts.forms import HoneypotMixin
from tours.models import Reservation


class ReservationForm(HoneypotMixin, forms.ModelForm):
    agree = forms.BooleanField(
        label='I understand my seat is held until Kaizen Safaris confirms it and payment is arranged.',
    )

    class Meta:
        model = Reservation
        fields = ('full_name', 'email', 'phone', 'country', 'travellers', 'message')
        labels = {'phone': 'Phone / WhatsApp', 'message': 'Special requests (diet, rooming, celebrations...)'}
        widgets = {
            'full_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
            'country': forms.TextInput(attrs={'autocomplete': 'country-name'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, departure, **kwargs):
        self.departure = departure
        super().__init__(*args, **kwargs)
        self.fields['travellers'].widget.attrs.update({'min': 1, 'max': max(departure.seats_left, 1)})

    def clean_travellers(self):
        n = self.cleaned_data['travellers']
        left = self.departure.seats_left
        if n > left:
            raise forms.ValidationError(f'Only {left} seat{"s" if left != 1 else ""} left on this departure.')
        return n
