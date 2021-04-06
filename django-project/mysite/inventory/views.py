from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, CreateView
from .models import (
    CustomerOrder, PurchaseOrder, Product, Customer, 
    InventoryRecord, ParStockRecord
)
from datetime import datetime

@login_required
def index(request):
    product_list = Product.objects.filter(user=request.user)
    calculated_inventories = []
    calculated_errors = []
    recent_inventories = []
    recent_par_stocks = []
    rpo_sums = []
    rco_sums = []
    for item in product_list:
        related_customer_orders = CustomerOrder.objects.filter(product=item)
        rco_sum = sum([customer_order.quantity for customer_order in related_customer_orders])
        related_purchase_orders = PurchaseOrder.objects.filter(product=item)
        rpo_sum = sum([purchase_order.total for purchase_order in related_purchase_orders])
        try:
            recent_inventory = InventoryRecord.objects.filter(product=item).order_by('-date').first().amount
        except:
            recent_inventory = 0
        try:
            recent_par_stock = ParStockRecord.objects.filter(product=item).order_by('-date').first().amount
        except:
            recent_par_stock = 0
        recent_inventories.append(recent_inventory)
        recent_par_stocks.append(recent_par_stock)
        calculated_inventories.append(recent_inventory + rpo_sum - rco_sum)
        calculated_errors.append(recent_inventory - recent_par_stock)
        rpo_sums.append(rpo_sum)
        rco_sums.append(rco_sum)

    context = {'product_inventories': zip(
        product_list, calculated_inventories, rpo_sums, 
        rco_sums, recent_inventories, recent_par_stocks, calculated_errors
        )}

    return render(request, 'inventory/index.html', context)

@login_required
def product_detail(request, product):
    product = Product.objects.get(label=product)
    related_customer_orders = CustomerOrder.objects.filter(product=product)
    rco_sum = sum([customer_order.quantity for customer_order in related_customer_orders])
    related_purchase_orders = PurchaseOrder.objects.filter(product=product)
    rpo_sum = sum([purchase_order.total for purchase_order in related_purchase_orders])
    try:
        recent_inventory = InventoryRecord.objects.filter(product=item).order_by('-date').first().amount
    except:
        recent_inventory = 0
    try:
        recent_par_stock = ParStockRecord.objects.filter(product=item).order_by('-date').first().amount
    except:
        recent_par_stock = 0
    calculated_inventory = recent_inventory + rpo_sum - rco_sum
    stock_error = recent_inventory - recent_par_stock
    context = {
        'product': product,
        'available': calculated_inventory,
        'customer_orders': rco_sum,
        'purchase_orders': rpo_sum,
        'recent_inventory': recent_inventory,
        'recent_par_stock': recent_par_stock,
        'stock_error': stock_error,
    }
    
    return render(request, 'inventory/product_detail.html', context)


@method_decorator(login_required, name='dispatch')
class ProductOrders(DetailView):
    template_name = 'inventory/product_order_detail.html'
    model = Product
    slug_field = 'label'
    slug_url_kwarg = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.product = self.get_object()
        self.related_customer_orders = CustomerOrder.objects.filter(product=self.product)
        self.related_purchase_orders = PurchaseOrder.objects.filter(product=self.product)
        try:
            self.recent_inventory_record = InventoryRecord.objects.filter(product=self.product).order_by('-date').first().amount
        except:
            self.recent_inventory_record = 0
        try:
            self.recent_par_stock_record = ParStockRecord.objects.filter(product=self.product).order_by('-date').first().amount
        except:
            self.recent_par_stock_record = 0
        rco_sum = sum([customer_order.quantity for customer_order in self.related_customer_orders])
        rpo_sum = sum([purchase_order.total for purchase_order in self.related_purchase_orders])
        calculated_inventory = self.recent_inventory_record + rpo_sum - rco_sum
        stock_error = self.recent_inventory_record - self.recent_par_stock_record
        
        context['product'] = self.product
        context['available'] = calculated_inventory
        context['customer_orders_total'] = rco_sum
        context['purchase_orders_total'] = rpo_sum
        context['inventory'] = self.recent_inventory_record
        context['par_stock'] = self.recent_par_stock_record
        context['stock_error'] = stock_error
        context['related_customer_orders'] = self.related_customer_orders
        context['related_purchase_orders'] = self.related_purchase_orders

        return context


@method_decorator(login_required, name='dispatch')
class ProductOrdersDateFilter(DetailView):
    template_name = 'inventory/product_order_detail.html'
    model = Product
    slug_field = 'label'
    slug_url_kwarg = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date = self.kwargs['date']
        try:
            end_date = self.kwargs['end_date']
        except:
            end_date = max(max([item.date for item in CustomerOrder.objects.all()]), max([item.date for item in PurchaseOrder.objects.all()]))
            context['end_date_unset'] = True
        
        self.product = self.get_object()
        self.related_customer_orders = CustomerOrder.objects.filter(product=self.product, date__range=[start_date, end_date]).order_by('date')
        self.related_purchase_orders = PurchaseOrder.objects.filter(product=self.product, date__range=[start_date, end_date]).order_by('date')
        try:
            self.recent_inventory_record = InventoryRecord.objects.filter(product=self.product).order_by('-date').first().amount
        except:
            self.recent_inventory_record = 0
        try:
            self.recent_par_stock_record = ParStockRecord.objects.filter(product=self.product).order_by('-date').first().amount
        except:
            self.recent_par_stock_record = 0
        rco_sum = sum([customer_order.quantity for customer_order in self.related_customer_orders])
        rpo_sum = sum([purchase_order.total for purchase_order in self.related_purchase_orders])
        calculated_inventory = self.recent_inventory_record + rpo_sum - rco_sum
        stock_error = self.recent_inventory_record - self.recent_par_stock_record
      
        context['product'] = self.product
        context['available'] = calculated_inventory
        context['customer_orders_total'] = rco_sum
        context['purchase_orders_total'] = rpo_sum
        context['inventory'] = self.recent_inventory_record
        context['par_stock'] = self.recent_par_stock_record
        context['stock_error'] = stock_error
        context['related_customer_orders'] = self.related_customer_orders
        context['related_purchase_orders'] = self.related_purchase_orders
        context['co_filter_count'] = self.related_customer_orders.count()
        context['po_filter_count'] = self.related_purchase_orders.count()
        context['start_date'] = start_date.date()
        try:
            context['end_date'] = end_date.date()
        except:
            context['end_date'] = end_date

        return context


@method_decorator(login_required, name='dispatch')
class ProductCustomerOrderList(ListView):
    template_name = 'inventory/product_customer_orders.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return CustomerOrder.objects.filter(product=self.product).order_by('date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context


@method_decorator(login_required, name='dispatch')
class ProductCustomerOrderDateFilterList(ListView):
    template_name = 'inventory/product_customer_orders.html'
    ordering = ['date']

    def get_queryset(self):
        start_date = self.kwargs['date']
        end_date = datetime.now()
        self.product = Product.objects.get(label=self.kwargs['product'])
        return CustomerOrder.objects.filter(product=self.product, date__range=[start_date, end_date]).order_by('date')

    def get_context_data(self, **kwargs):
        co_count = self.get_queryset().count()
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        context['co_filter_count'] = co_count
        context['filter_date'] = self.kwargs['date'].date()
        return context


@method_decorator(login_required, name='dispatch')
class ProductPurchaseOrderList(ListView):
    template_name = 'inventory/product_purchase_orders.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return PurchaseOrder.objects.filter(product=self.product).order_by('date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product

        return context


@method_decorator(login_required, name='dispatch')
class CustomerCustomerOrderList(ListView):
    template_name = 'inventory/customer_customer_orders.html'
    
    def get_queryset(self):
        self.customer = get_object_or_404(Customer, label=self.kwargs['customer'])
        return CustomerOrder.objects.filter(
            customer=self.customer, product__user=self.request.user
            ).order_by('date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.customer

        return context


@method_decorator(login_required, name='dispatch')
class PurchaseOrderDetail(DetailView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_order_detail.html'


@method_decorator(login_required, name='dispatch')
class PurchaseOrderList(ListView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_orders.html'
    ordering = ['date']

    def get_queryset(self):
        return PurchaseOrder.objects.filter(product__user=self.request.user)

    def get_context_data(self, **kwargs):
        po_count = self.get_queryset().count()
        context = super().get_context_data(**kwargs)
        context['po_count'] = po_count
        return context


@method_decorator(login_required, name='dispatch')
class PurchaseOrderDateFilterList(ListView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_orders.html'
    ordering = ['date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po_count = self.get_queryset().count()
        context['po_filter_count'] = po_count
        context['start_date'] = self.kwargs['date'].date()
        try:
            context['end_date'] = self.end_date.date()
        except:
            context['end_date'] = self.end_date
        context['end_date_set'] = self.end_date_set
        return context

    def get_queryset(self):
        self.start_date = self.kwargs['date']
        try:
            self.end_date = self.kwargs['end_date']
            self.end_date_set = True
        except:
            self.end_date = max([item.date for item in CustomerOrder.objects.all()])
            self.end_date_set = False
        return PurchaseOrder.objects.filter(
            product__user=self.request.user,
            date__range=[self.start_date, self.end_date]).order_by('date')
        

@method_decorator(login_required, name='dispatch')
class CustomerOrderDateFilterList(ListView):
    model = CustomerOrder
    template_name = 'inventory/customer_orders.html'
    ordering = ['date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        co_count = self.get_queryset().count()
        context['co_filter_count'] = co_count
        context['start_date'] = self.start_date.date()
        try:
            context['end_date'] = self.end_date.date()
        except:
            context['end_date'] = self.end_date
        context['end_date_set'] = self.end_date_set
        return context

    def get_queryset(self):
        self.start_date = self.kwargs['date']
        try:
            self.end_date = self.kwargs['end_date']
            self.end_date_set = True
        except:
            self.end_date = max([item.date for item in CustomerOrder.objects.all()])
            self.end_date_set = False
        return CustomerOrder.objects.filter(
            product__user=self.request.user,
            date__range=[self.start_date, self.end_date]).order_by('date')


@method_decorator(login_required, name='dispatch')
class CustomerOrderDetail(DetailView):
    model = CustomerOrder
    template_name = 'inventory/customer_order_detail.html'


@method_decorator(login_required, name='dispatch')
class CustomerOrderList(ListView):
    model = CustomerOrder
    template_name = 'inventory/customer_orders.html'
    ordering = ['date', 'product']

    def get_queryset(self):
        return CustomerOrder.objects.filter(product__user=self.request.user)

    def get_context_data(self, **kwargs):
        co_count = self.get_queryset().count()
        context = super().get_context_data(**kwargs)
        context['co_count'] = co_count
        return context


@method_decorator(login_required, name='dispatch')
class PurchaseOrderCreate(CreateView):
    model = PurchaseOrder
    fields = ['order_number', 'product', 'runs', 'run_quantity', 'date']


@method_decorator(login_required, name='dispatch')
class ProductCreate(CreateView):
    model = Product
    fields = ['name', 'label']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

