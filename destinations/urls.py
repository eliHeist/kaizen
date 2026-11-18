from django.urls import path

from destinations import views

app_name = 'destinations'

urlpatterns = [
    path('', views.destination_list, name='list'),
    path('<slug:slug>/', views.destination_detail, name='detail'),
    path('<slug:destination>/<slug:slug>/', views.place_detail, name='place'),
]
