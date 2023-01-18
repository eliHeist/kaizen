from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.generic import TemplateView, FormView

from rest_framework.decorators import api_view
from rest_framework.response import Response

from contacts.forms import BookingForm, CarHireForm, TentHireForm
from contacts.models import Receipient


class BookingView(FormView):
   form_class = BookingForm
   success_url = '/contact/booking/success'
   template_name = 'contacts/booking.html'

   def post(self, request, *args, **kwargs):
      form_class = self.get_form_class()
      form = self.get_form(form_class)

      if form.is_valid():
         return self.form_valid(form)
      print('here2')
      return self.form_invalid(form)

   def form_valid(self, form):
      form.send_mail()
      return super(BookingView, self).form_valid(form)

   def form_invalid(self, form):
      # form.send_mail()
      return super(BookingView, self).form_invalid(form)
   

class TentHireView(FormView):
   form_class = TentHireForm
   success_url = '/contact/booking/success'
   template_name = 'contacts/tent-hire.html'

   def post(self, request, *args, **kwargs):
      form_class = self.get_form_class()
      form = self.get_form(form_class)
      print(form)

      return self.form_valid(form) if form.is_valid() else self.form_invalid(form)

   def form_valid(self, form):
      form.send_mail()
      return super(TentHireView, self).form_valid(form)

   def form_invalid(self, form):
      print('here2')
      print('here2')
      # form.send_mail()
      return super(TentHireView, self).form_invalid(form)
   

class CarHireView(FormView):
   form_class = CarHireForm
   success_url = '/contact/booking/success'
   template_name = 'contacts/car-hire.html'

   def post(self, request, *args, **kwargs):
      form_class = self.get_form_class()
      form = self.get_form(form_class)

      print(form)

      if form.is_valid():
         return self.form_valid(form)
      print('here2')
      return self.form_invalid(form)

   def form_valid(self, form):
      form.send_mail()
      return super(CarHireView, self).form_valid(form)

   def form_invalid(self, form):
      # form.send_mail()
      return super(CarHireView, self).form_invalid(form)


@api_view(['POST'])
def sendMail(request):
   if request.method == 'POST':
      data = request.data
      print(data)
      message = f"Name: {data.get('name')}\nEmail: {data.get('email')}\nMessage: {data.get('message')}"
      message = f"Name: {data.get('name')}\nEmail: {data.get('email')}\nMessage: {data.get('message')}"
      print("\n\nmessage\n"+message)
      receipients = Receipient.objects.all()

      try:
         send_mail(
            subject='Sent from footer form',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[receipient.email for receipient in receipients]
         )

         return Response('SUCCESS')
      except Exception as e:
         print(f'Exception: {e}')
         return Response('Failed')


# @api_view(['POST'])
# def bookNow(request):
#    message = 'Successfully sent your booking'
#    context = {
#       'message': message
#    }
#    template_name = 'contacts/status.html'
# def bookNow(request):
#    message = 'Successfully sent your booking'
#    context = {
#       'message': message
#    }
#    template_name = 'contacts/status.html'
   
#    if request.method == 'POST':
#       data = request.data
#       print(data)
#       message = f'''Name: {data.get('fname')} {data.get('lname')}
#       \nEmail: {data.get('email')} \t Phone number: {data.get('phone')}
#       \nWhen are you planning to visit: {data.get('date')}
#       \nHow many are you?: {data.get('single_number')}
#       \nIf a group, How many People are in the group?: {data.get('group_number')}
#       \nWhich Tour or Visit are you intrested in?: {data.get('tour')}
#       \nWhat's the best way to contact you?: {data.get('fav-means')}
#       \nIf phone what is the best time to call you?: {data.get('fav-time')}
#       \nAnything Else we should know: {data.get('anything_else')}
#       '''
#       print("\n\nmessage\n"+message)
#       receipients = Receipient.objects.all()

#       try:
#          send_mail(
#             subject='Booking',
#             message=message,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[receipient.email for receipient in receipients]
#          )
#       try:
#          send_mail(
#             subject='Booking',
#             message=message,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[receipient.email for receipient in receipients]
#          )

#       except Exception as e:
#          print(f'Exception: {e}')
#          message = "Failed, try again later"

#    return render(request, template_name, context)
#    return render(request, template_name, context)


class SuccessView(TemplateView):
   template_name = "contacts/success.html"
