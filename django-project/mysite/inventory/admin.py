from django.contrib import admin
from .models import Product, PurchaseOrder, Customer, CustomerOrder

admin.site.register(Product)
admin.site.register(PurchaseOrder)
admin.site.register(CustomerOrder)
admin.site.register(Customer)
