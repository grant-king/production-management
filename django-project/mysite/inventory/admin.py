from django.contrib import admin
from .models import Product, PurchaseOrder, Customer, CustomerOrder, InventoryRecord, ParStockRecord

admin.site.register(Product)
admin.site.register(PurchaseOrder)
admin.site.register(CustomerOrder)
admin.site.register(Customer)
admin.site.register(InventoryRecord)
admin.site.register(ParStockRecord)
