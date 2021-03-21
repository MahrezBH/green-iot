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
        context['plan'] = 'monthly' if user.plan == settings.STRIPE_PLAN_ANNUAL_ID else 'annually'
        context['current_plan'] = 'annually' if user.plan == settings.STRIPE_PLAN_ANNUAL_ID else 'monthly'
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
    context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
    context['customer_email'] = request.user.email
    context['stripe_plan_id'] = stripe_plan_id
    return render(request, 'payment/card.html', context)

@login_required
def payment_result(request):
    payment_method_id = request.POST['payment_method_id']
    stripe_plan_id = request.POST['stripe_plan_id']
    stripe.api_key = API_KEY
    user = User.objects.filter(email=request.user.email).first()
    customer = stripe.Customer.create(
                email=request.user.email,
                payment_method=payment_method_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
    s = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    'plan': stripe_plan_id
                },
            ]
        )
    user.plan = stripe_plan_id
    user.stripe_customer = customer.id
    user.stripe_subscription = s.id
    user.save()
    latest_invoice = stripe.Invoice.retrieve(s.latest_invoice)
    payment_intent = stripe.PaymentIntent.retrieve(latest_invoice.payment_intent)
    if payment_intent.status == 'requires_action':
        pi = stripe.PaymentIntent.retrieve(
                latest_invoice.payment_intent
            )
        context = {}
        context['payment_intent_secret'] = pi.client_secret
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
        return render(request, 'payment/3dsecure.html', context)
    messages.success(request, f'Thank you for your purchase!')
    return redirect('/')

def changeSubscription(request):
    stripe.api_key = API_KEY
    subscription = stripe.Subscription.retrieve(request.user.stripe_subscription)
    plan_id = settings.STRIPE_PLAN_MONTHLY_ID if subscription['items']['data'][0].plan.id == settings.STRIPE_PLAN_ANNUAL_ID else settings.STRIPE_PLAN_ANNUAL_ID
    stripe.Subscription.modify(
        subscription.id,
        cancel_at_period_end=False,
        proration_behavior='create_prorations',
        items=[{
            'id': subscription['items']['data'][0].id,
            'plan': plan_id
        }])
    user = User.objects.filter(email=request.user.email).first()
    user.plan = plan_id
    user.save()
    messages.success(request, f'Your Subscription changed successfully!')
    return redirect('/')

def set_paid_until(event):
    stripe.api_key = API_KEY 
    customer = event.data.object.customer
    try:
        user = User.objects.get(stripe_customer=customer)
    except User.DoesNotExist:
        logger.warning(
            f"User with customer #{customer} not found"
        ) 
        return False
    if 'current_period_end' in event.data.object:
        user.set_paid_until(event.data.object.current_period_end)
    else:
        user.set_paid_until(event.data.object.lines.data[0].period.end)

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
    if event.type in ['invoice.paid', 'customer.subscription.updated']:
        set_paid_until(event)
    return HttpResponse(status=200)