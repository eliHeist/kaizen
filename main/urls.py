from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('humans.txt', views.humans_txt, name='humans'),
]
