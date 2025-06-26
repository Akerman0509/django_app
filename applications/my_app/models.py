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
    
# --- The Customer "Type" ------------------------------------------------------------
    
class Customer(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

# --- The Product "Type" ---
class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    stock = models.PositiveIntegerField(default=0, help_text="Total number of items in stock")
   
    def __str__(self):
        return f"{self.name} "
    
# # --- The Individual Inventory Item ---
# class StockItem(models.Model):

#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
#     serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
#     added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     def __str__(self):
#         return f"Item of {self.product.name} "
    
    
class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    name = models.CharField(max_length=200, default='Default Cart Name')
    
    products= models.ManyToManyField(Product, through='CartItem', related_name='carts')
    
    def __str__(self):
        return f"Cart of {self.customer.name}"
    
class CartItem(models.Model):
    
   # REQUIRED: A ForeignKey to the source model (Cart)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    
    # REQUIRED: A ForeignKey to the target model (Product)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Your extra data for the relationship
    quantity = models.PositiveIntegerField(default=1)
    # Storing unit_price at time of adding to cart is good practice
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the product at the time it was added to the cart") 
    checkout_status = models.BooleanField(default=False, help_text="Indicates if the item has been checked out")
    

        
class Receipt(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='receipts')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for {self.cart.customer.name} - Total: {self.total_amount}"
    
    
class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='product_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} at {self.unit_price} each"