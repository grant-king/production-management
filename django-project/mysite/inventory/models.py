from django.db import models
from django.urls import reverse
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=40)
    label = models.SlugField(max_length=40, null=True)

    def __str__(self):
        return f'{self.name}'


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


class InventoryRecord(models.Model):
    amount = models.IntegerField()
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.amount} {self.product.name} on {self.date}'


class ParStockRecord(models.Model):
    amount = models.IntegerField()
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.amount} {self.product.name} on {self.date}'
