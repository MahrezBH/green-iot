from django.urls import path
from .views import *

urlpatterns = [
    path('upgrade', upgrade, name='upgrade'),
    path('payment_result', payment_result, name='payment_result'),
    path('stripe_payment', stripe_payment, name='stripe_payment'),
    path('stripe_webhook', stripe_webhook, name='stripe_webhook'),
    path('change_subscription', changeSubscription,name='change_subscription')
]