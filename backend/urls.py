from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/v1/users/', include('main.urls.user_urls')),
    path('api/v1/videos/', include('main.urls.video_urls')),
    path('api/v1/channels/', include('main.urls.channel_urls')),
    path('api/v1/subscribers/', include('main.urls.subscriber_urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
