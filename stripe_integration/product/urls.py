from django.urls import path
from product.views import *

urlpatterns = [
    path('',productListView, name='product_list'),
    path('checkout/<int:product_id>/', CheckoutView, name='checkout'),
    path('create-payment/<int:product_id>/', createPaymentView, name='create_payment'),
    path('success/',success,name='success'),
    path('cancel/',cancel,name='cancel'),
    path('stripe-webhook/', stripeWebhookView, name='stripe_webhook')
]