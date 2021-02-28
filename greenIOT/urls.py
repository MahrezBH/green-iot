from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'GreenIOT administration'
admin.site.index_title = 'GreenIOT'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('customer/', include('customer.urls')),
    path('accounts/', include("allauth.urls")),
]
