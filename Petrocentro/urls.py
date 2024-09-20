from django.contrib import admin
from django.urls import *
from django.conf.urls import handler404
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('paginaPetrocentro.urls')),
    path('', include('blogs.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('', include('users.urls')),
    path('', include('configuracion.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root= settings.STATIC_ROOT)