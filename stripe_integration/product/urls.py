from django.urls import path
from product.views import *

urlpatterns = [
    path('',productListView, name='product_list'),
]