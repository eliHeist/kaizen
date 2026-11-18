from django.urls import path

from tours import views

app_name = 'tours'

urlpatterns = [
    path('', views.tour_list, name='list'),
    path('departures/', views.departure_list, name='departures'),
    path('styles/<slug:slug>/', views.style_detail, name='style'),
    path('reservation/<str:reference>/', views.reserved, name='reserved'),
    path('<slug:slug>/', views.tour_detail, name='detail'),
    path('<slug:slug>/reserve/<int:pk>/', views.reserve, name='reserve'),
]
