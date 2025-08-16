"""
URL configuration for glidego project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

    # Redirect root URL to the Swagger docs
    path('', RedirectView.as_view(url='api/docs/')),
    

    # API base URLs
    path('api/', include([
        # path('admin/', admin.site.urls),
        path('', lambda request: HttpResponse("🎉 It works!")),
        path("Authuser/", include('AuthUser.urls')),
        path("Hotel/", include('Hotel.urls')),
        path("Destination/", include('Destination.urls')),
        path("Cabs/", include('Cabs.urls')),

    ])),

    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
