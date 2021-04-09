from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=40)
    label = models.SlugField(max_length=40, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('inventory:product_detail', kwargs={'product': self.label})


class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=10)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    runs = models.FloatField()
    run_quantity = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f'{self.order_number}: {self.product.name}: {self.total}'

    @property
    def total(self):
        return self.run_quantity * self.runs
    
    def get_absolute_url(self):
        return reverse('inventory:purchase_order_detail', kwargs={'pk': self.pk})


class Customer(models.Model):
    name = models.CharField(max_length=40)
    label = models.SlugField(max_length=40, null=True)

    def __str__(self):
        return f'{self.name}'


class CustomerOrder(models.Model):
    order_number = models.CharField(max_length=10)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    date = models.DateField()
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.order_number}: {self.customer.name[:5]}: {self.quantity} {self.product.name}'

    def get_absolute_url(self):
        return reverse('inventory:customer_order_detail', kwargs={'pk': self.pk})


class InventoryRecord(models.Model):
    amount = models.IntegerField()
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.amount} {self.product.name} on {self.date}'

    def get_absolute_url(self):
        return reverse('inventory:inventory_record_detail', kwargs={
            'pk': self.pk, 'product': self.product.label})


class ParStockRecord(models.Model):
    amount = models.IntegerField()
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.amount} {self.product.name} on {self.date}'

    def get_absolute_url(self):
        return reverse('inventory:par_stock_record_detail', kwargs={
            'pk': self.pk, 'product': self.product.label})

