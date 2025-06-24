from django.db import models
from django.utils import timezone
import datetime


# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, related_name='books')
    category = models.ManyToManyField(Category,blank=True , related_name='books')
    in_stock = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    
class Customer(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
  
class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField('CartItem', blank=True, related_name='cart_items')
    name = models.CharField(max_length=200, default='Default Cart Name')
    def __str__(self):
        return f"Cart of {self.customer.name}"
    
class CartItem(models.Model):
    product = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} at {self.unit_price} each"
    
    