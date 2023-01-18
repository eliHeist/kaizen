# from main.models import Subscriber
from django import forms
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.conf import settings

from contacts.models import Receipient


# class NewsletterForm(forms.ModelForm):
#     class Meta:
#         model = Subscriber
#         fields = (
#             'email',
#         )

class ContactForm(forms.Form):
    your_name = forms.CharField(required=False)
    your_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    your_message = forms.CharField(widget=forms.Textarea, required=True)
    # message = forms.CharField(widget=forms.Textarea, required=True)

    def send_email(self, subject, email, text, name):
        subject = subject
        email = email
        text = text
        name = name
        message = f"{name}: {email}\n\n{text}"

        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, ['amartislab@gmail.com','elijahtriumph@amartislab.com','support@amartislab.com'], fail_silently=False)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

CONTACT_CHOICES = [
    ('Email', 'Email'),
    ('Phone', 'Phone'),
    ('Either', 'Either'),
]

TIME_CHOICES = [
    ('8AM - 11AM', '8AM - 4AM'),
    ('12PM - 4PM', '12PM - 4PM'),
    ('5PM - 10PM', '5PM - 10PM'),
]

SLEEPER_CHOICES = [
    ('1-2 Sleeper', '1-2 Sleeper'),
    ('3-4 Sleeper', '3-4 Sleeper'),
]

CAR_CHOICES = [
    ('7-8 seater', '7-8 seater'),
    ('4 seater', '4 seater'),
    ('6 seater', '6 seater'),
]

class BookingForm(forms.Form):
    first_name = forms.CharField(label='First Name', required=True)
    last_name = forms.CharField(label='Last Name', required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Phone Number', max_length=15, required=False)
    visit_date = forms.DateField(label='When are you planning to visit?', widget=forms.SelectDateWidget)
    no = forms.IntegerField(label='How many are you?', required=False)
    group_no = forms.IntegerField(label='If a group, How many People are in the group?', required=False)
    tour = forms.CharField(label='Which Tour or Visit are you intrested in?', required=False)
    contact_choice = forms.ChoiceField(label="What's the best way to contact you?", choices=CONTACT_CHOICES, widget=forms.RadioSelect, required=False)
    time_choice = forms.ChoiceField(label='If phone what is the best time to call you? (EAT)', choices=TIME_CHOICES, widget=forms.RadioSelect, required=False)
    more_info = forms.CharField(label='Anything Else we should know', widget=forms.Textarea, required=False)

    def send_mail(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        phone = self.cleaned_data.get('phone')
        visit_date = self.cleaned_data.get('visit_date')
        no = self.cleaned_data.get('no')
        group_no = self.cleaned_data.get('group_no')
        tour = self.cleaned_data.get('tour')
        contact_choice = self.cleaned_data.get('contact_choice')
        time_choice = self.cleaned_data.get('time_choice')
        more_info = self.cleaned_data.get('more_info')

        try:
            message = f'Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nWhen they want to visit: {visit_date}\nNumber of people: {no}\nNumber in group: {group_no}\nTour interested in: {tour}\nPrefered contact method: {contact_choice}\nPrefered time of contact: {time_choice}\nMore information: {more_info}'
            subject = 'Booking'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [r.email for r in Receipient.objects.all()], fail_silently=False)
            # print(message)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')


class TentHireForm(forms.Form):
    first_name = forms.CharField(label='First Name', required=True)
    last_name = forms.CharField(label='Last Name', required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Phone Number', max_length=15, required=True)
    sleepers = forms.ChoiceField(label="Tent type", choices=SLEEPER_CHOICES, widget=forms.RadioSelect, required=False)
    contact_choice = forms.ChoiceField(label="What's the best way to contact you?", choices=CONTACT_CHOICES, widget=forms.RadioSelect, required=False)
    time_choice = forms.ChoiceField(label='If phone what is the best time to call you? (EAT)', choices=TIME_CHOICES, widget=forms.RadioSelect, required=False)
    more_info = forms.CharField(label='Anything Else we should know', widget=forms.Textarea, required=False)

    def send_mail(self):
        print('sending')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        phone = self.cleaned_data.get('phone')
        tent = self.cleaned_data.get('sleepers')
        contact_choice = self.cleaned_data.get('contact_choice')
        time_choice = self.cleaned_data.get('time_choice')
        more_info = self.cleaned_data.get('more_info')

        try:
            message = f'Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nAction: hire {tent} tent\n\nPrefered contact method: {contact_choice}\nPrefered time of contact: {time_choice}\nMore information: {more_info}'
            subject = 'Tent Hire'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [r.email for r in Receipient.objects.all()], fail_silently=False)
            # print(message)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')


class CarHireForm(forms.Form):
    first_name = forms.CharField(label='First Name', required=True)
    last_name = forms.CharField(label='Last Name', required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Phone Number', max_length=15, required=True)
    vehicle = forms.ChoiceField(label="Number of seats of vehicle", choices=CAR_CHOICES, widget=forms.RadioSelect, required=False)
    contact_choice = forms.ChoiceField(label="What's the best way to contact you?", choices=CONTACT_CHOICES, widget=forms.RadioSelect, required=False)
    time_choice = forms.ChoiceField(label='If phone what is the best time to call you? (EAT)', choices=TIME_CHOICES, widget=forms.RadioSelect, required=False)
    more_info = forms.CharField(label='Anything Else we should know', widget=forms.Textarea, required=False)

    def send_mail(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        phone = self.cleaned_data.get('phone')
        vehicle = self.cleaned_data.get('vehicle')
        contact_choice = self.cleaned_data.get('contact_choice')
        time_choice = self.cleaned_data.get('time_choice')
        more_info = self.cleaned_data.get('more_info')

        try:
            message = f'Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nAction: hire {vehicle} vehicle\n\nPrefered contact method: {contact_choice}\nPrefered time of contact: {time_choice}\nMore information: {more_info}'
            subject = 'Car Hire'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [r.email for r in Receipient.objects.all()], fail_silently=False)
            # print(message)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

# class ContactForm(forms.Form):
#     your_name = forms.CharField(required=False)
#     your_email = forms.EmailField(required=True)
#     subject = forms.CharField(required=True)
#     your_message = forms.CharField(widget=forms.Textarea, required=True)
#     # message = forms.CharField(widget=forms.Textarea, required=True)

#     def send_email(self):
#         subject = self.cleaned_data.get('subject')
#         email = self.cleaned_data.get('your_email')
#         text = self.cleaned_data.get('your_message')
#         name = self.cleaned_data.get('your_name')
#         message = f"{name}: {email}\n\n{text}"
#         print(message)

#         try:
#             send_mail(subject, message, settings.EMAIL_HOST_USER, ['amartissebaggala@gmail.com','eliyang256@outlook.com', 'kayimaoscul@gmail.com', 'ogocharles231@gmail.com'], fail_silently=False)
#         except BadHeaderError:
#             return HttpResponse('Invalid header found.')