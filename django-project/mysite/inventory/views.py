from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.generic import (
    DetailView, ListView, CreateView, UpdateView, DeleteView)
from .models import (
    CustomerOrder, PurchaseOrder, Product, Customer, 
    InventoryRecord, ParStockRecord)
from datetime import datetime
from django.db.models import ProtectedError
from django.db import IntegrityError

@login_required
def index(request):
    product_list = Product.objects.filter(user=request.user)
    has_customers = Customer.objects.filter(user=request.user)
    has_purchase_orders = 0
    has_customer_orders = 0
    calculated_inventories = []
    calculated_errors = []
    recent_inventories = []
    recent_par_stocks = []
    rpo_sums = []
    rco_sums = []
    for item in product_list:
        related_customer_orders = CustomerOrder.objects.filter(product=item)
        has_customer_orders += related_customer_orders.count()
        rco_sum = sum([customer_order.quantity for customer_order in related_customer_orders])
        related_purchase_orders = PurchaseOrder.objects.filter(product=item)
        has_purchase_orders += related_purchase_orders.count()
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
        available_product = recent_inventory + rpo_sum - rco_sum
        calculated_inventories.append(available_product)
        calculated_errors.append(available_product - recent_par_stock)
        rpo_sums.append(rpo_sum)
        rco_sums.append(rco_sum)

    context = {'product_inventories': zip(
        product_list, calculated_inventories, rpo_sums, 
        rco_sums, recent_inventories, recent_par_stocks, calculated_errors
        ), 'has_customers': has_customers,
        'has_customer_orders': has_customer_orders,
        'has_purchase_orders': has_purchase_orders}

    return render(request, 'inventory/index.html', context)


class ProductDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'inventory/product_detail.html'
    model = Product
    query_pk_and_slug = True
    slug_field = 'label'
    slug_url_kwarg = 'product'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        self.product = self.get_object()
        related_customer_orders = CustomerOrder.objects.filter(product=self.product)
        rco_sum = sum([customer_order.quantity for customer_order in related_customer_orders])
        related_purchase_orders = PurchaseOrder.objects.filter(product=self.product)
        rpo_sum = sum([purchase_order.total for purchase_order in related_purchase_orders])
        try:
            recent_inventory = InventoryRecord.objects.filter(product=self.product).order_by('-date').first().amount
        except:
            recent_inventory = 0
        try:
            recent_par_stock = ParStockRecord.objects.filter(product=self.product).order_by('-date').first().amount
        except:
            recent_par_stock = 0
        calculated_inventory = recent_inventory + rpo_sum - rco_sum
        stock_error = calculated_inventory - recent_par_stock
        
        context['product'] = self.product
        context['available'] = calculated_inventory
        context['customer_orders'] = rco_sum
        context['purchase_orders'] = rpo_sum
        context['recent_inventory'] = recent_inventory
        context['recent_par_stock'] = recent_par_stock
        context['stock_error'] = stock_error

        return context

    def test_func(self):
        if self.get_object().user == self.request.user:
            return True
        else:
            return False


class ProductOrders(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'inventory/product_order_detail.html'
    model = Product
    query_pk_and_slug = True
    slug_field = 'label'
    slug_url_kwarg = 'product'

    def get_context_data(self, *args, **kwargs):
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
        stock_error = calculated_inventory - self.recent_par_stock_record
        
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

    def test_func(self):
        if self.get_object().user == self.request.user:
            return True
        else:
            return False


class ProductOrdersDateFilter(LoginRequiredMixin, UserPassesTestMixin, DetailView):
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

    def test_func(self):
        if self.get_object().user == self.request.user:
            return True
        else:
            return False


class ProductCustomerOrderList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'inventory/product_customer_orders.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return CustomerOrder.objects.filter(product=self.product).order_by('date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False


class ProductCustomerOrderDateFilterList(LoginRequiredMixin, UserPassesTestMixin, ListView):
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

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False


class ProductPurchaseOrderList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'inventory/product_purchase_orders.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return PurchaseOrder.objects.filter(product=self.product).order_by('date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product

        return context

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False


class CustomerCustomerOrderList(LoginRequiredMixin, UserPassesTestMixin, ListView):
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

    def test_func(self):
        try:
            if self.get_queryset().first().customer.user == self.request.user:
                return True
            else:
                return False
        except AttributeError:
            return False


class PurchaseOrderDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_order_detail.html'

    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class PurchaseOrderList(LoginRequiredMixin, UserPassesTestMixin, ListView):
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

    def test_func(self):
        if self.get_queryset().count() == 0:
            return True
        elif self.get_queryset().first().product.user == self.request.user:
            return True
        else:
            return False


class PurchaseOrderDateFilterList(LoginRequiredMixin, UserPassesTestMixin, ListView):
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

    def test_func(self):
        if self.get_queryset().first().product.user == self.request.user:
            return True
        else:
            return False
        

class CustomerOrderDateFilterList(LoginRequiredMixin, UserPassesTestMixin, ListView):
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
    
    def test_func(self):
        if self.get_queryset().first().product.user == self.request.user:
            return True
        else:
            return False


class CustomerOrderDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomerOrder
    template_name = 'inventory/customer_order_detail.html'

    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class CustomerOrderList(LoginRequiredMixin, UserPassesTestMixin, ListView):
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

    def test_func(self):
        if self.get_queryset().count() == 0:
            return True
        elif self.get_queryset().first().product.user == self.request.user:
            return True
        else:
            return False


class PurchaseOrderCreate(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    fields = ['order_number', 'runs', 'run_quantity', 'date']

    def form_valid(self, form):
        form.instance.product = Product.objects.get(label=self.kwargs['product'])
        return super().form_valid(form)


class PurchaseOrderUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PurchaseOrder
    fields = ['order_number', 'product', 'runs', 'run_quantity', 'date']

    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super(PurchaseOrderUpdate, self).get_form()
        form.fields['product'].queryset = Product.objects.filter(user=self.request.user)
        return form


class PurchaseOrderDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PurchaseOrder
    
    def get_success_url(self):
        return reverse_lazy(
        'inventory:product_orders', 
        kwargs={'product': self.get_object().product.label})
    
    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class ProductCreate(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name']

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            form.instance.label = slugify(form.instance.name)
            return super().form_valid(form)
        except IntegrityError:
            form.instance.label = slugify(f'{form.instance.name}_{self.request.user.id}')
            return super().form_valid(form)


class ProductUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'label']
    slug_field = 'label'
    slug_url_kwarg = 'product'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        if self.get_object().user == self.request.user:
            return True
        else:
            return False


class ProductDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    slug_field = 'label'
    slug_url_kwarg = 'product'

    def test_func(self):
        if self.get_object().user == self.request.user:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('inventory:index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return redirect(self.get_success_url())
        except:
            return render(request, 'inventory/protected_delete_error.html')


class CustomerOrderCreate(LoginRequiredMixin, CreateView):
    model = CustomerOrder
    fields = ['order_number', 'customer', 'date', 'quantity']

    def form_valid(self, form):
        form.instance.product = Product.objects.get(label=self.kwargs['product'])
        return super().form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super(CustomerOrderCreate, self).get_form()
        form.fields['customer'].queryset = Customer.objects.filter(user=self.request.user)
        return form


class CustomerOrderUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomerOrder
    fields = ['order_number', 'customer', 'product', 'date', 'quantity']

    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super(CustomerOrderUpdate, self).get_form()
        form.fields['customer'].queryset = Customer.objects.filter(user=self.request.user)
        form.fields['product'].queryset = Product.objects.filter(user=self.request.user)
        return form


class CustomerOrderDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CustomerOrder

    def get_success_url(self):
        return reverse_lazy(
        'inventory:product_orders', 
        kwargs={'product': self.get_object().product.label})
    
    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class ProductInventoryRecordList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'inventory/product_inventory_records.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return InventoryRecord.objects.filter(product=self.product).order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False


class InventoryRecordDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = InventoryRecord
    template_name = 'inventory/inventory_record_detail.html'

    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class InventoryRecordCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = InventoryRecord
    fields = ['amount', 'date']

    def form_valid(self, form):
        form.instance.product = Product.objects.get(label=self.kwargs['product'])
        return super().form_valid(form)

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False
    

class InventoryRecordUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InventoryRecord
    fields = ['amount', 'date']

    def form_valid(self, form):
        form.instance.product = Product.objects.get(label=self.kwargs['product'])
        return super().form_valid(form)

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False


class InventoryRecordDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = InventoryRecord

    def get_success_url(self):
        return reverse_lazy(
        'inventory:product_inventory_records', 
        kwargs={'product': self.get_object().product.label})
    
    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class ProductParStockRecordList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'inventory/product_par_stock_records.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return ParStockRecord.objects.filter(product=self.product).order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False


class ParStockRecordDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ParStockRecord
    template_name = 'inventory/par_stock_record_detail.html'

    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class ParStockRecordCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ParStockRecord
    fields = ['amount', 'date']

    def form_valid(self, form):
        form.instance.product = Product.objects.get(label=self.kwargs['product'])
        return super().form_valid(form)

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False
    

class ParStockRecordUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ParStockRecord
    fields = ['amount', 'date']

    def form_valid(self, form):
        form.instance.product = Product.objects.get(label=self.kwargs['product'])
        return super().form_valid(form)

    def test_func(self):
        if Product.objects.get(label=self.kwargs['product']).user == self.request.user:
            return True
        else:
            return False


class ParStockRecordDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ParStockRecord

    def get_success_url(self):
        return reverse_lazy(
        'inventory:product_par_stock_records', 
        kwargs={'product': self.get_object().product.label})
    
    def test_func(self):
        if self.get_object().product.user == self.request.user:
            return True
        else:
            return False


class CustomerList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'inventory/customers.html'
    
    def get_queryset(self):
        self.customer_list = Customer.objects.filter(user=self.request.user)
        return self.customer_list

    def test_func(self):
        if self.get_queryset().count() == 0:
            return True
        elif self.get_queryset().first().user == self.request.user:
            return True
        else:
            return False


class CustomerDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Customer
    template_name = 'inventory/customer_detail.html'

    def test_func(self):
        customer = self.get_object()
        if customer.user == self.request.user:
            return True
        else:
            return False


class CustomerCreate(LoginRequiredMixin, CreateView):
    model = Customer
    fields = ['name']

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            form.instance.label = slugify(form.instance.name)
            return super().form_valid(form)
        except IntegrityError:
            form.instance.label = slugify(f'{form.instance.name}_{self.request.user.id}')
            return super().form_valid(form)
    

class CustomerUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Customer
    fields = ['name', 'label']

    def form_valid(self, form):
        form.instance.label = slugify(form.instance.label)
        return super().form_valid(form)

    def test_func(self):
        if self.get_object().user == self.request.user:
            return True
        else:
            return False


class CustomerDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Customer

    def get_success_url(self):
        return reverse_lazy('inventory:my_customers')
    
    def test_func(self):
        if self.get_object().user == self.request.user:
            return True
        else:
            return False
        
    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
            return redirect(self.get_success_url())
        except ProtectedError:
            return render(request, 'inventory/protected_delete_error.html')