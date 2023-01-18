from django.urls import path

from contacts.views import BookingView, CarHireView, SuccessView, TentHireView, sendMail
app_name = 'contacts'

urlpatterns = [
    path('sendmail/', sendMail, name='send_mail'),
    path('booking/', BookingView.as_view(), name='book_now'),
    path('booking/success/', SuccessView.as_view(), name='success'),
    path('forms/tents/', TentHireView.as_view(), name='tent-hire'),
    path('forms/cars/', CarHireView.as_view(), name='car-hire'),
]