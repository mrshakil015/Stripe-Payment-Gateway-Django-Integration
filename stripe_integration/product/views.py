from django.shortcuts import render
from product.models import *

def productListView(request):
    product_data = ProductModel.objects.all()
    
    context = {
        "product_data":product_data,
    }
    
    return render(request, 'products.html', context)