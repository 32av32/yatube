from django.contrib import admin
from django.urls import path, include
from yatube import settings
from django.contrib.flatpages import views as fp_views
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('about-us/', fp_views.flatpage, {'url': '/about-us/'}, name='about_us'),
    path('technology/', fp_views.flatpage, {'url': '/technology/'}, name='technology'),
    path('', include('posts.urls')),
]

handler404 = 'posts.views.page_not_found' # noqa
handler500 = 'posts.views.server_error' # noqa

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)