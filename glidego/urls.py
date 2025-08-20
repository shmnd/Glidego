from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.generic import RedirectView


schema_view             = get_schema_view(
        openapi.Info(
        title             = "glideGo API",
        default_version   = 'v1',
        description       = "system that helps manage various aspects of a hotels's operations",
        terms_of_service  = "",
        contact           = openapi.Contact(email="shamnad.p@happyclicks.in"),
    ),
    public               = True,
    permission_classes   = [permissions.AllowAny],
)
urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='api/docs/')),


    path('api/', include([
        # Redirect root URL to the Swagger docs
        # path('', RedirectView.as_view(url='api/docs/')),
        # path('admin/', admin.site.urls),
        
        path('', lambda request: HttpResponse("🎉 It works!")),
        path("Authuser/", include('AuthUser.urls')),
        path("Hotel/", include('Hotel.urls')),
        path("Destination/", include('Destination.urls')),
        path("cab/", include('Cabs.urls')),
        path("activity/",include('Activity.urls')),
        path("planner/",include('Planner.urls')),

    ])),

    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
