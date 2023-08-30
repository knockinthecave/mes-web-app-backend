from django.contrib import admin
from django.urls import path, include  # <- Don't forget to import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # <- Add this line to include the URL patterns from your api app
]
