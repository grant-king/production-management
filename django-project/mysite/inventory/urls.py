from django.urls import path, register_converter
from . import views
from inventory.views import (
    ProductCustomerOrderList, ProductPurchaseOrderList, PurchaseOrderList,
    ProductDetail, CustomerCustomerOrderList, PurchaseOrderDetail, 
    CustomerOrderDetail, CustomerOrderList, PurchaseOrderDateFilterList,
    CustomerOrderDateFilterList, ProductCustomerOrderDateFilterList, 
    ProductOrders, ProductOrdersDateFilter, PurchaseOrderCreate, ProductCreate,
    ProductUpdate, PurchaseOrderUpdate, PurchaseOrderDelete, ProductDelete,
    CustomerOrderCreate, CustomerOrderUpdate, CustomerOrderDelete,
    ProductInventoryRecordList, InventoryRecordDetail, InventoryRecordCreate,
    InventoryRecordUpdate, InventoryRecordDelete, ProductParStockRecordList,
    ParStockRecordDetail, ParStockRecordCreate, ParStockRecordUpdate, 
    ParStockRecordDelete, CustomerList, CustomerDetail, CustomerCreate, 
    CustomerUpdate, CustomerDelete,
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
    path('customer_orders/<slug:product>/new/', CustomerOrderCreate.as_view(), name='customer_order_create'),
    path('customer_orders/product/<slug:product>/', ProductCustomerOrderList.as_view(), name='product_customer_orders'),
    path('customer_orders/product/<slug:product>/date/<yyyy:date>/', ProductCustomerOrderDateFilterList.as_view(), name='date_filter_product_customer_orders'),
    path('customer_orders/<int:pk>/', CustomerOrderDetail.as_view(), name='customer_order_detail'),
    path('customer_orders/<int:pk>/update/', CustomerOrderUpdate.as_view(), name='customer_order_update'),
    path('customer_orders/<int:pk>/delete/', CustomerOrderDelete.as_view(), name='customer_order_delete'),
    path('customer_orders/all/', CustomerOrderList.as_view(), name='all_customer_orders'),
    path('purchase_orders/product/<slug:product>/', ProductPurchaseOrderList.as_view(), name='product_purchase_orders'),
    path('purchase_orders/<slug:product>/new/', PurchaseOrderCreate.as_view(), name='purchase_order_create'),
    path('purchase_orders/<int:pk>/', PurchaseOrderDetail.as_view(), name='purchase_order_detail'),
    path('purchase_orders/<int:pk>/update/', PurchaseOrderUpdate.as_view(), name='purchase_order_update'),
    path('purchase_orders/<int:pk>/delete/', PurchaseOrderDelete.as_view(), name='purchase_order_delete'),
    path('purchase_orders/all/', PurchaseOrderList.as_view(), name='all_purchase_orders'),
    path('customers/all/', CustomerList.as_view(), name='my_customers'),
    path('customers/<int:pk>/', CustomerDetail.as_view(), name='customer_detail'),
    path('customers/new/', CustomerCreate.as_view(), name='customer_create'),
    path('customers/<int:pk>/update/', CustomerUpdate.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', CustomerDelete.as_view(), name='customer_delete'),
    path('customers/<slug:customer>/customer_orders', CustomerCustomerOrderList.as_view(), name='customer_customer_orders'),
    path('products/new/', ProductCreate.as_view(), name='product_create'),
    path('products/<slug:product>/', ProductDetail.as_view(), name='product_detail'),
    path('products/<slug:product>/update/', ProductUpdate.as_view(), name='product_update'),
    path('products/<slug:product>/delete/', ProductDelete.as_view(), name='product_delete'),
    path('productorders/<slug:product>/', ProductOrders.as_view(), name='product_orders'),
    path('productorders/<slug:product>/<yyyy:date>/', ProductOrdersDateFilter.as_view(), name='date_filter_product_orders'),
    path('productorders/<slug:product>/<yyyy:date>/<yyyy:end_date>/', ProductOrdersDateFilter.as_view(), name='date_range_filter_product_orders'),
    path('purchase_orders/<yyyy:date>/', PurchaseOrderDateFilterList.as_view(), name='date_filter_purchase_orders'),
    path('purchase_orders/<yyyy:date>/<yyyy:end_date>/', PurchaseOrderDateFilterList.as_view(), name='date_range_filter_purchase_orders'),
    path('customer_orders/<yyyy:date>/', CustomerOrderDateFilterList.as_view(), name='date_filter_customer_orders'),
    path('customer_orders/<yyyy:date>/<yyyy:end_date>/', CustomerOrderDateFilterList.as_view(), name='date_range_filter_customer_orders'),
    path('inventory_records/<slug:product>/', ProductInventoryRecordList.as_view(), name='product_inventory_records'),
    path('inventory_records/<slug:product>/<int:pk>/', InventoryRecordDetail.as_view(), name='inventory_record_detail'),
    path('inventory_records/<slug:product>/new/', InventoryRecordCreate.as_view(), name='inventory_record_create'),
    path('inventory_records/<slug:product>/<int:pk>/update', InventoryRecordUpdate.as_view(), name='inventory_record_update'),
    path('inventory_records/<slug:product>/<int:pk>/delete', InventoryRecordDelete.as_view(), name='inventory_record_delete'),
    path('par_stock_records/<slug:product>/', ProductParStockRecordList.as_view(), name='product_par_stock_records'),
    path('par_stock_records/<slug:product>/<int:pk>/', ParStockRecordDetail.as_view(), name='par_stock_record_detail'),
    path('par_stock_records/<slug:product>/new/', ParStockRecordCreate.as_view(), name='par_stock_record_create'),
    path('par_stock_records/<slug:product>/<int:pk>/update', ParStockRecordUpdate.as_view(), name='par_stock_record_update'),
    path('par_stock_records/<slug:product>/<int:pk>/delete', ParStockRecordDelete.as_view(), name='par_stock_record_delete'),
]
