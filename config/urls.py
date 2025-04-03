from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('crm/', include('crm.urls')),
    path('pos/', include('pos.urls')),
    path('auth/', include('personnels.urls')),
    path('inbox/notifications/', include('notifications.urls', namespace='notifications')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

