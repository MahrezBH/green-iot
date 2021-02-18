from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import User

AdminSite.enable_nav_sidebar=False

admin.site.register(User)
