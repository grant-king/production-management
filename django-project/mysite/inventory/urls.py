from django.urls import path, register_converter
from . import views
from inventory.views import (
    ProductCustomerOrderList, ProductPurchaseOrderList, PurchaseOrderList,
    product_detail, CustomerCustomerOrderList, PurchaseOrderDetail, 
    CustomerOrderDetail, CustomerOrderList, PurchaseOrderDateFilterList,
    CustomerOrderDateFilterList, ProductCustomerOrderDateFilterList, 
    ProductOrders, ProductOrdersDateFilter, 
)
from datetime import datetime


class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value


register_converter(DateConverter, 'yyyy')

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),
    path('customer_orders/product/<slug:product>/', ProductCustomerOrderList.as_view(), name='product_customer_orders'),
    path('customer_orders/product/<slug:product>/date/<yyyy:date>/', ProductCustomerOrderDateFilterList.as_view(), name='date_filter_product_customer_orders'),
    path('customer_orders/<int:pk>/', CustomerOrderDetail.as_view(), name='customer_order_detail'),
    path('customer_orders/all/', CustomerOrderList.as_view(), name='all_customer_orders'),
    path('purchase_orders/product/<slug:product>/', ProductPurchaseOrderList.as_view(), name='product_purchase_orders'),
    path('purchase_orders/<int:pk>/', PurchaseOrderDetail.as_view(), name='purchase_order_detail'),
    path('purchase_orders/all/', PurchaseOrderList.as_view(), name='all_purchase_orders'),
    path('customers/<customer>/', CustomerCustomerOrderList.as_view(), name='customer_customer_orders'),
    path('products/<product>/', views.product_detail, name='product_detail'),
    path('productorders/<slug:product>/', ProductOrders.as_view(), name='product_orders'),
    path('productorders/<slug:product>/<yyyy:date>/', ProductOrdersDateFilter.as_view(), name='date_filter_product_orders'),
    path('productorders/<slug:product>/<yyyy:date>/<yyyy:end_date>/', ProductOrdersDateFilter.as_view(), name='date_range_filter_product_orders'),
    path('purchase_orders/<yyyy:date>/', PurchaseOrderDateFilterList.as_view(), name='date_filter_purchase_orders'),
    path('purchase_orders/<yyyy:date>/<yyyy:end_date>/', PurchaseOrderDateFilterList.as_view(), name='date_range_filter_purchase_orders'),
    path('customer_orders/<yyyy:date>/', CustomerOrderDateFilterList.as_view(), name='date_filter_customer_orders'),
    path('customer_orders/<yyyy:date>/<yyyy:end_date>/', CustomerOrderDateFilterList.as_view(), name='date_range_filter_customer_orders'),
]
