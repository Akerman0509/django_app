from django.contrib import admin



from .models import Author, Publisher, Book, Category, Customer, Cart, CartItem, Product, Receipt, ReceiptItem

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', "book_num" ]
    search_fields = ('name',)
    @admin.display(
        description='Number of Books',
    )
    def book_num(self, obj):
        return obj.books.count()
    
@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'address',"address_state"]
    search_fields = ('name',)
    
    @admin.display(
        description="address_state",
    )
    def address_state(self,obj):
        return obj.address if obj.address else "No Address"
        
    
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
    
    
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'price', 'author', 'publisher', "author__name", "in_stock")
    search_fields = ('title',)
    list_filter = ('author', 'publisher', 'category')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'customer__name')
    search_fields = ('user__name',)
    
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart__name','product', 'quantity', 'unit_price', 'checkout_status')
    search_fields = ('product__title',)
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock')
    search_fields = ('name',)
    
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart__name', 'created_at', 'total_amount')
    search_fields = ('cart__customer_id__name',)
    
@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'receipt__id', 'receipt','product__name','quantity', 'unit_price')
    search_fields = ('product__name',)