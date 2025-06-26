from statistics import quantiles

from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
import logging
from django.http import HttpResponse
logger = logging.getLogger(__name__)

from .models import Author, Publisher, Category, Book
from .serializers import AuthorSerializer, PublisherSerializer, CategorySerializer, BookSerializer, ValidateAuthorSerializer, CustomerSerializer, CartItemSerializer, ReceiptSerializer
from django.core.cache import cache

import redis
import json
from django.conf import settings
from datetime import datetime, timezone
import base64
import hashlib
import hmac
import jwt
from django.contrib.auth import authenticate
import os
# import decorator

from .decorators import jwt_required
# Initialize Redis connection
r = redis.Redis(host='localhost', port=6379, db=1)


@api_view(['GET'])
def get_author(request):
    """
    This is a simple view that returns the author of the API.
    """
    # queryset = cache.get('authors')
    # if not queryset:
    #     authors = Author.objects.all()
    #     serializer = AuthorSerializer(authors, many=True)
    #     cache.set('authors', serializer.data, timeout=60*15)
    # else:
    #     print (f"[getAuthor] Cache hit for authors: {queryset}")
    #     serializer = AuthorSerializer(queryset, many=True)
    queryset = r.get('authors')
    if not queryset:
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        r.set('authors', json.dumps(serializer.data), ex=60*15)
    else:
        print(f"[getAuthor] Cache hit for authors")
        queryset = json.loads(queryset)
        serializer = AuthorSerializer(queryset, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
def get_book(request):
    """
    This is a simple view that returns the book of the API.
    """
    key = 'books'
    cached = r.get(key)
    
    if not cached:
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        data = serializer.data
        r.set(key,json.dumps(data).encode('utf-8'), ex=60*15)
    else:
        print(f"[getBook] Cache hit for books")
        cached = json.loads(cached.decode('utf-8'))
        serializer = BookSerializer(cached, many=True)
    
    
    
    
    return Response(serializer.data)


@api_view(['GET'])
@jwt_required
def get_publisher(request):
    """
    This is a simple view that returns the publisher of the API.
    """
    queryset = cache.get('publishers')
    if not queryset:
        publishers = Publisher.objects.all()
        serializer = PublisherSerializer(publishers, many=True)
        cache.set('publishers', serializer.data, timeout=60*15)
    else:
        print (f"[getPublisher] Cache hit for publishers: {queryset}")
        serializer = PublisherSerializer(queryset, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
@jwt_required
def get_category(request):
    """
    This is a simple view that returns the category of the API.
    """
    queryset = cache.get('categories')
    if not queryset:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        cache.set('categories', serializer.data, timeout=60*15)
    else:
        print (f"[getCategory] Cache hit for categories: {queryset}")
        serializer = CategorySerializer(queryset, many=True)
    
    return Response(serializer.data)


@api_view(['POST'])
def add_author(request):
    """
    This is a simple view that adds an author to the API.
    """
    
    logger.info("[addAuthor] Received data: %s", request.data)
    
    serializer = ValidateAuthorSerializer(data=request.data)
    
    if serializer.is_valid():
        author = serializer.save()
        logger.info("[addAuthor] Author created: %s", author)
        return Response(serializer.data, status=201)
    
    logger.warning("[addAuthor] Validation failed: %s", serializer.errors)
    return Response(serializer.errors, status=400)



@api_view(['POST'])
def login(request):
    """
    This is a simple view that handles user login.
    """
    logger.info("[login] Received data: %s", request.data)

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"message": "Username and password required"}, status=400)

    # 🔐 Authenticate user
    user = authenticate(username=username, password=password)

    if user is not None:
        # Optional: check if user.is_active
        logger.info("[login] Authenticated user: %s", user.username)
        access_token = create_jwt_token(user, algorithm='HS256')  # 3 minutes expiration-------------------------
        print(f"[login] JWT token created : {access_token}")
        return Response({
            "message": "Login successful", 
            "user_id": user.id,
            "username": user.username,
            "access_token": access_token,
            }, status=200)
        
        # return Response({"message": "Login successful"}, status=200)
    else:
        logger.warning("[login] Failed login attempt for user: %s", username)
        return Response({"message": "Invalid credentials"}, status=401)


def create_jwt_token(user, algorithm, exp=5*60):
    header = {
        "typ": "JWT",
        "alg": algorithm
    }

    payload = {
        "user_id": user.id,
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": datetime.now(timezone.utc).timestamp() + exp
    }
    print(f"payload: {payload}")

    def base64url_encode(data):
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    if algorithm == 'HS256':
        # Manual construction for HS256
        encoded_header = base64url_encode(json.dumps(header).encode('utf-8'))
        encoded_payload = base64url_encode(json.dumps(payload).encode('utf-8'))
        unsigned_token = f"{encoded_header}.{encoded_payload}".encode('utf-8')

        secret_key = settings.SECRET_KEY.encode('utf-8')
        signature = base64url_encode(hmac.new(secret_key, unsigned_token, hashlib.sha256).digest())

        jwt_token = f"{encoded_header}.{encoded_payload}.{signature}"
        return jwt_token

    elif algorithm == 'RS256':
        # Use PyJWT to build the full token
        private_key_path = os.path.join(settings.BASE_DIR, 'private.key')
        with open(private_key_path, 'r') as f:
            private_key = f.read()
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256')
        return jwt_token

    else:
        raise ValueError("Unsupported algorithm. Use 'HS256' or 'RS256'.")
    
@api_view(['GET'])
def public_key_view(request):
    key_path = os.path.join(settings.BASE_DIR, 'public_client.key')
    with open(key_path, 'r') as f:
        public_key = f.read()
    return HttpResponse(public_key, content_type='text/plain')


@api_view(['POST'])
def add_to_cart(request):
    """
    This is a simple view that adds an item to the cart.
    """
    serializer = CartItemSerializer(data=request.data)
    
    if serializer.is_valid():
        cart_item = serializer.save()
        logger.info("[add_to_cart] cart item created: %s", cart_item)
        return Response(serializer.data, status=201)
    
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def checkout(request):
    serializer = ReceiptSerializer(data=request.data)
    if serializer.is_valid():
        receipt = serializer.save()
        logger.info("[checkout] Receipt created: %s", receipt)
        return Response(serializer.data, status=201)
    
    return Response(serializer.errors, status=400)
