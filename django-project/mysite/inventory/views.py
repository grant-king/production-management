from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from .models import CustomerOrder, PurchaseOrder, Product

def index(request):
    product_list = Product.objects.all()
    calculated_inventories = []
    rpo_sums = []
    rco_sums = []
    for item in product_list:
        related_customer_orders = CustomerOrder.objects.filter(product=item)
        rco_sum = sum([customer_order.quantity for customer_order in related_customer_orders])
        related_purchase_orders = PurchaseOrder.objects.filter(product=item)
        rpo_sum = sum([purchase_order.total for purchase_order in related_purchase_orders])
        calculated_inventories.append(item.back_stock + rpo_sum - rco_sum)
        rpo_sums.append(rpo_sum)
        rco_sums.append(rco_sum)

    context = {'product_inventories': zip(product_list, calculated_inventories, rpo_sums, rco_sums)}

    return render(request, 'inventory/index.html', context)


class ProductCustomerOrderList(ListView):
    template_name = 'inventory/product_customer_orders.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return CustomerOrder.objects.filter(product=self.product)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product

        return context


class ProductPurchaseOrderList(ListView):
    template_name = 'inventory/product_purchase_orders.html'
    
    def get_queryset(self):
        self.product = get_object_or_404(Product, label=self.kwargs['product'])
        return PurchaseOrder.objects.filter(product=self.product)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product

        return context
