from django.shortcuts import render, redirect, get_object_or_404
from product.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def productListView(request):
    product_data = ProductModel.objects.all()
    
    context = {
        "product_data":product_data,
    }
    
    return render(request, 'product/products.html', context)

def CheckoutView(request, product_id):
    product = get_object_or_404(ProductModel, id=product_id)
    
    context = {
        'product': product
    }
    return render(request, 'product/checkout.html', context)

def success(request):
    
    return render(request,'product/payment-success.html')

def cancel(request):
    
    return render(request,'product/payment-cancel.html')

def createPaymentView(request, product_id):
    YOUR_DOMAIN = "http://127.0.0.1:8000"
    product = get_object_or_404(ProductModel, id=product_id)
    order = OrderModel.objects.create(
        user = request.user,
        product=product,
        amount = product.price
    )

    checkout_session = stripe.checkout.Session.create(
        line_items=[{
            'price_data':{
                'currency':'usd',
                'unit_amount': int(product.price * 100),
                'product_data':{
                    'name': product.name
                }
            },
            'quantity': 1,
        }],
        mode='payment',
        customer_email = request.user.email,
        success_url=YOUR_DOMAIN + "/success/",
        cancel_url=YOUR_DOMAIN + "/cancel/",
    )
    
    order.stripe_checkout_session_id = checkout_session.id
    order.save()
    return redirect(checkout_session.url)
    
@csrf_exempt
def stripeWebhookView(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print(f'Error parsing payload: {e}')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f'Error verifying webhook signature: {e}')
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("✅ PaymentIntent succeeded:", session['id'])

        try:
            order = OrderModel.objects.get(
                stripe_checkout_session_id=session['id']
            )
            order.is_paid = True
            order.save()
            product = order.product
            product.stock -= 1
            product.save()
            print('Order marked as paid!')
            return redirect('success')
        except OrderModel.DoesNotExist:
            print("⚠️ Order not found for PaymentIntent:", session['id'])

        return redirect('success')

    return JsonResponse({"status": "unhandled_event"})