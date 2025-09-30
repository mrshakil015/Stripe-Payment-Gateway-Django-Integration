from django.urls import path
from product.views import *

urlpatterns = [
    path('',productListView, name='product_list'),
    path('checkout/<int:product_id>/', CheckoutView, name='checkout'),
    path('success/',success,name='success'),
    path('cancel/',cancel,name='cancel'),
]