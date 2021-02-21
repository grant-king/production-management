from django.urls import path, register_converter
from . import views
from inventory.views import (
    ProductCustomerOrderList, ProductPurchaseOrderList, PurchaseOrderList,
    product_detail, CustomerCustomerOrderList, PurchaseOrderDetail, 
    CustomerOrderDetail, CustomerOrderList, PurchaseOrderDateFilterList,
    CustomerOrderDateFilterList,
)
from datetime import datetime


class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value


register_converter(DateConverter, 'yyyy')

urlpatterns = [
    path('', views.index, name='index'),
    path('customer_orders/product/<slug:product>/', ProductCustomerOrderList.as_view(), name='product_customer_orders'),
    path('customer_orders/<int:pk>/', CustomerOrderDetail.as_view(), name='customer_order_detail'),
    path('customer_orders/all/', CustomerOrderList.as_view(), name='all_customer_orders'),
    path('purchase_orders/product/<slug:product>/', ProductPurchaseOrderList.as_view(), name='product_purchase_orders'),
    path('purchase_orders/<int:pk>/', PurchaseOrderDetail.as_view(), name='purchase_order_detail'),
    path('purchase_orders/all/', PurchaseOrderList.as_view(), name='all_purchase_orders'),
    path('customers/<customer>/', CustomerCustomerOrderList.as_view(), name='customer_customer_orders'),
    path('products/<product>/', views.product_detail, name='product_detail'),
    path('purchase_orders/date/<yyyy:date>/', PurchaseOrderDateFilterList.as_view(), name='date_filter_purchase_orders'),
    path('customer_orders/date/<yyyy:date>/', CustomerOrderDateFilterList.as_view(), name='date_filter_customer_orders'),
]
