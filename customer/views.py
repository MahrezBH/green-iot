from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import stripe
from django.conf import settings
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseRedirect
)
from .models import User
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import redirect

API_KEY = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

@login_required
def upgrade(request):
    context = {}
    user = User.objects.get(email=request.user.email)
    if user.is_paid():
        context = {'user':user, 'paid':True}
    return render(request, 'payment/upgrade.html',context)

@require_POST
@login_required
def stripe_payment(request):
    stripe.api_key = API_KEY
    context = {}
    plan = request.POST.get('plan','m')
    stripe_plan_id = amount = 0
    if plan == 'm':
        stripe_plan_id = settings.STRIPE_PLAN_MONTHLY_ID
        amount = 100
    else:
        stripe_plan_id = settings.STRIPE_PLAN_ANNUAL_ID
        amount = 1000

    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='usd',
        payment_method_types=['card']
    )
    context['secret_key'] = payment_intent.client_secret
    context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
    context['customer_email'] = request.user.email
    context['payment_intent_id'] = payment_intent.id
    context['stripe_plan_id'] = stripe_plan_id
    return render(request, 'payment/card.html', context)

@login_required
def payment_result(request):
    payment_intent_id = request.POST['payment_intent_id']
    payment_method_id = request.POST['payment_method_id']
    stripe_plan_id = request.POST['stripe_plan_id']
    stripe.api_key = API_KEY
    result = stripe.PaymentIntent.confirm(payment_intent_id, payment_method=payment_method_id)
    if result.status == 'requires_action':
        pi = stripe.PaymentIntent.retrieve(payment_intent_id)
        context = {}
        context['payment_intent_secret'] = pi.client_secret
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
        return render(request, 'payment/3dsecure.html',context)
    messages.success(request, f'Thank you for your purchase!')
    return redirect('/')

def set_paid_until(charge):
    stripe.api_key = API_KEY
    pi = stripe.PaymentIntent.retrieve(charge.payment_intent)
    if charge.amount == 100:
        added_days = 31
    else:
        added_days = 365
    email = charge.billing_details.email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning(
            f"User with email {email} not found"
        )
        return False
    user.paid_until = datetime.today() + timedelta(days=added_days)
    user.save()


@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SIGNING_KEY
        )
        logger.info("Event constructed correctly")
    except ValueError:
        # Invalid payload
        logger.warning("Invalid Payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        logger.warning("Invalid signature")
        return HttpResponse(status=400)
    # Handle the event
    if event.type == 'charge.succeeded':
        # object has  payment_intent attr
        set_paid_until(event.data.object)
    return HttpResponse(status=200)