from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag'),
    path('author/<slug:slug>/', views.author_detail, name='author'),
    path('<slug:slug>/', views.post_detail, name='detail'),
]
