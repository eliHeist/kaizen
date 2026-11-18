from django.urls import path

from contacts import views

app_name = 'contacts'

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('plan-your-trip/', views.plan_trip, name='plan'),
    path('thank-you/', views.thanks, name='thanks'),
]
