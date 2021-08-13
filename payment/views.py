import json
import os
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from basket.basket import Basket
from orders.views import payment_confirmation

from orders.models import Order


def order_placed(request):
    basket = Basket(request)
    basket.clear()

    order_key = Order.objects.first().order_key
    print("order_key: ", order_key)

    # Just for DEBUG CASE (ALTERNATIVE TO STRIPE WEBHOOKS)
    # IN PROD NEED TO REMOVE BELOW LINE QUERY
    Order.objects.filter(order_key=order_key).update(billing_status=True)
    return render(request, "payment/orderplaced.html")


class Error(TemplateView):
    template_name = "payment/error.html"


@login_required
def BasketView(request):


    print("Basket View Called")
    basket = Basket(request)
    total = str(basket.get_total_price())
    total = total.replace(".", "")
    total = int(total)

    # stripe.api_key = "sk_test_51BbYtuJMWp5ChnxjRM6t9vQvB4P2hMUqaXc3CORwOJ4EfVJ7QpZy61Rqe59WBOkiN0gJvfbckZsfV33T9TUnVqKt00An6UjSQW"
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=total, currency="gbp", metadata={"userid": request.user.id}
    )

    print("Basket View Called now Returning: ")
    print("STRIPE_SECRET_KEY: ", settings.STRIPE_SECRET_KEY)
    print("STRIPE_PUBLISHABLE_KEY: ", os.environ.get("STRIPE_PUBLISHABLE_KEY"))
    return render(
        request,
        "payment/payment_form.html",
        {
            "client_secret": intent.client_secret,
            "STRIPE_PUBLISHABLE_KEY": os.environ.get("STRIPE_PUBLISHABLE_KEY"),
        },
    )


@csrf_exempt
def stripe_webhook(request):
    print("STRIPE WEBHOOK CALLED")
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)

    print("EVENT: ", event)

    # Handle the event
    if event.type == "payment_intent.succeeded":
        payment_confirmation(event.data.object.client_secret)

    else:
        print("Unhandled event type {}".format(event.type))

    return HttpResponse(status=200)
