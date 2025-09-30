from django.contrib import admin
from product.models import ProductModel, OrderModel

@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock")
    search_fields = ("name",)
    list_filter = ("price",)
    
@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id",'user', 'product', 'amount', 'is_paid', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ("is_paid","created_at")