# Serializers define the API representation.
from rest_framework import serializers
from .models import Author, Publisher, Category, Book, Customer, Cart, CartItem, Product, Receipt, ReceiptItem

from .validators import validate_name
import re
from django.db import transaction





class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields =  '__all__'


class ValidateAuthorSerializer(serializers.Serializer):
    firstname = serializers.CharField(write_only=True)
    lastname = serializers.CharField(write_only=True)
  
    email = serializers.EmailField(write_only = True)    


    def validate(self,data):
        print (f"validating data: {data}")
        
        if not re.match (validate_name.regex, data['firstname']):
            raise serializers.ValidationError({"name": "Invalid first_name: Only alphabetic characters are allowed."})
        if not re.match (validate_name.regex, data['lastname']):
            raise serializers.ValidationError({"name": "Invalid last_name: Only alphabetic characters are allowed."})
        
        fullname = data.get('firstname') + ' ' + data.get('lastname')
        print(f"validating fullname: {fullname}")
        
        return data
    
    def create(self, validated_data):
        print(f"creating author: {validated_data}")
        firstname = validated_data.pop('firstname')
        lastname = validated_data.pop('lastname')
        fullname = firstname + ' ' + lastname
        author = Author.objects.create(name=fullname, **validated_data)
        return author
        
    def to_representation(self, instance):
        parts = instance.name.split()
        return {
            "firstname": parts[0],
            "lastname": " ".join(parts[1:]),
            "email": instance.email
        }
        

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields =  '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields =  '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    publisher = PublisherSerializer()
    category = CategorySerializer(many=True)

    class Meta:
        model = Book
        fields =  '__all__'
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields =  '__all__'
        
class CartItemSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField( write_only= True)
    product_id = serializers.IntegerField(write_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    class Meta:
        model = CartItem
        fields = ('id', 'customer_id', 'product_id', 'quantity', 'unit_price')
    
    def validate(self, data):
        print (f"Validating CartItem data: {data}")
        customer_id = data.get('customer_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        unit_price = data.get('unit_price')

        # Validate that the customer exists
        if not Customer.objects.filter(id=customer_id).exists():
            raise serializers.ValidationError("Customer does not exist.")

        # Validate that the product exists
        if not Product.objects.filter(id=product_id).exists():
            raise serializers.ValidationError("Product does not exist.")
        
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        
        if not unit_price or unit_price <= 0:
            data['unit_price'] = Product.objects.get(id=product_id).price

        return data
    
    def create(self, validated_data):
        print (validated_data)
        customer_id = validated_data.pop('customer_id')
        product_id = validated_data.pop('product_id')
        # Get the customer
        customer = Customer.objects.get(id=customer_id)
        # Get the customer's cart
        if not hasattr(customer, 'cart'):
            raise serializers.ValidationError("Customer does not have a cart.")
        
        # Get the product
        product = Product.objects.get(id=product_id)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=customer.cart,
            product=product,
            checkout_status=False,
            defaults={
                'quantity': validated_data['quantity'],
                'unit_price': validated_data['unit_price']
            }
        )
        if not created:
            # If the item already exists, update the quantity and unit price
            cart_item.quantity += validated_data['quantity']
            cart_item.save()
        
        return cart_item
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'cart_id': instance.cart.id,
            'product_id': instance.product.id,
            'product_name': instance.product.name,
            'quantity': instance.quantity,
            'unit_price': str(instance.unit_price),
        }

        
class CartSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ('items',)
        

# {
#     "customer_id": ,
# }
class ReceiptSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Receipt
        fields = 'id', 'customer_id', 'total_amount', 'created_at'
        read_only_fields = ('id', 'total_amount', 'created_at')
        
    def validate(self, data):
        # check if cart exists for the customer and if it has items
        customer_id = data.get('customer_id')
        if not Customer.objects.filter(id=customer_id).exists():
            raise serializers.ValidationError("Customer does not exist.")
        if not Cart.objects.filter(customer_id=customer_id).exists():
            raise serializers.ValidationError("Customer does not have a cart.")
        cart = Cart.objects.get(customer_id=customer_id)
        if not cart.items.exists():
            raise serializers.ValidationError("Customer's cart is empty.")
        
        return data
    
    # create new cart and auto copy cart items to receipt items
    def update_stock(self, cart_items):
        # This method now takes the original cart_items
        
        # Get all product IDs we need to work with
        product_ids = [item.product_id for item in cart_items]
        
        # --- THIS IS THE MOST IMPORTANT PART ---
        # Lock the relevant product rows in the database for the duration of this transaction.
        # No other request can modify these specific rows until this transaction is complete.
        products_to_update = Product.objects.select_for_update().filter(id__in=product_ids)
        
        # Create a dictionary for easy lookup: {product_id: product_object}
        product_map = {p.id: p for p in products_to_update}
        
        # Check stock levels for all items first
        for item in cart_items:
            product = product_map.get(item.product_id)
            if product is None:
                # This should not happen if the cart is valid, but it's a good safeguard
                raise serializers.ValidationError(f"Product with ID {item.product_id} not found.")
                
            if product.stock < item.quantity:
                raise serializers.ValidationError(f"Not enough stock for product '{product.name}'. Available: {product.stock}, Requested: {item.quantity}")

        # If all checks pass, prepare the stock updates
        for item in cart_items:
            product = product_map.get(item.product_id)
            # Update the stock on the Python object, change checkout status
            product.stock -= item.quantity

        # Use bulk_update for an efficient, single database query to save all changes
        Product.objects.bulk_update(products_to_update, ['stock'])
        
            
    @transaction.atomic
    def create(self, validated_data):
        customer_id = validated_data.pop('customer_id')
        customer = Customer.objects.get(id=customer_id)
        cart = customer.cart
        # Get all cart items that are NOT yet checked out.
        # This prevents re-processing items if something goes wrong.
        cart_items = cart.items.filter(checkout_status=0)
        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty or all items have been processed.")
        # --- STAGE 1: Handle Stock ---
        # This will lock the products, check stock, and update if all is good.
        # If there's not enough stock, it will raise a ValidationError and the
        # whole transaction will be rolled back. Nothing will be created or updated.
        self.update_stock(cart_items)
        # create receipt
        receipt = Receipt.objects.create(cart=cart, total_amount=0)
        total_amount = 0
        
        # create receipt items from cart items
        receipt_items_to_create = []
        
        for cart_item in cart_items:
            total_amount += cart_item.quantity * cart_item.unit_price
            receipt_items_to_create.append(
                ReceiptItem(
                    receipt=receipt,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                )
            )
        
        receipt_items = ReceiptItem.objects.bulk_create(receipt_items_to_create)
        # update receipt total amount
        receipt.total_amount = total_amount
        receipt.save()    
        
        
            # --- STAGE 3: UPDATE CART ITEM STATUS ---
        # Instead of deleting, we now update their status.
        # This is much better than deleting.
        cart_items.update(checkout_status=1)
        
        return receipt

class ReceiptItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptItem
        fields = ('id', 'receipt', 'product', 'quantity', 'unit_price')
        
