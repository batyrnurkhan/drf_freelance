from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/', include('chats.urls')),
    path('api/listings/', include('listings.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
