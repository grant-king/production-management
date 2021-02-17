from django.urls import path
from . import views
from inventory.views import ProductCustomerOrderList, ProductPurchaseOrderList, product_detail, CustomerCustomerOrderList

urlpatterns = [
    path('', views.index, name='index'),
    path('customer_orders/<product>/', ProductCustomerOrderList.as_view(), name='product_customer_orders'),
    path('purchase_orders/<product>/', ProductPurchaseOrderList.as_view(), name='product_purchase_orders'),
    path('customers/<customer>/', CustomerCustomerOrderList.as_view(), name='customer_customer_orders'),
    path('products/<product>/', views.product_detail, name='product_detail'),
]
