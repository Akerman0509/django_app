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
    address = models.CharField(max_length=200)

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
    
    def __str__(self):
        return self.title
    
    

