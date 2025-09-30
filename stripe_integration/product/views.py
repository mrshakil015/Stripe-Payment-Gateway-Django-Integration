from django.shortcuts import render, redirect, get_object_or_404
from product.models import *
from django.http import JsonResponse

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