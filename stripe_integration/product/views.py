from django.shortcuts import render, redirect, get_object_or_404
from product.models import *
from django.http import JsonResponse
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
    
    return JsonResponse({"status":"Success"})

def cancel(request):
    
    return JsonResponse({"status":"Cancel"})

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
    