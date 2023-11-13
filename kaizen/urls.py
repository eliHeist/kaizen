from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf.urls import handler500

handler500 = 'main.views.server_error500'
handler404 = 'main.views.error404View'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("main.urls", namespace='main')),
    path('destinations/', include("destinations.urls", namespace='destinations')),
    path('api/', include("api.urls", namespace='api')),
    path('contact/', include("contacts.urls", namespace='contacts')),
]

# handling the 404 error


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
