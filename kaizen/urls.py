from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from main.sitemaps import sitemaps

handler404 = 'main.views.error_404'
handler500 = 'main.views.error_500'

admin.site.site_header = 'Kaizen Safaris'
admin.site.site_title = 'Kaizen Safaris admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', include('main.urls', namespace='main')),
    path('destinations/', include('destinations.urls', namespace='destinations')),
    path('tours/', include('tours.urls', namespace='tours')),
    path('rentals/', include('rentals.urls', namespace='rentals')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('', include('contacts.urls', namespace='contacts')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
