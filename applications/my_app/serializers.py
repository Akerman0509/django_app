# Serializers define the API representation.
from rest_framework import serializers
from .models import Author, Publisher, Category, Book

from .validators import validate_name
import re





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