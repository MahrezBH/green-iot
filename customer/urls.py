from django.urls import path
from .views import *

urlpatterns = [
    path('login', MyLoginView.as_view(), name='account_login'),
]