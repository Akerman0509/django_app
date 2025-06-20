from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from django.urls import path

app_name = "my_app"
urlpatterns = [
    # get
    path("authors/", views.get_author, name="getAuthor"),
    path("books/", views.get_book, name="getBook"),
    path("publishers/", views.get_publisher, name="getPublisher"),
    path("categories/", views.get_category, name="getCategory"),
    
    
    # post
    path("author/add/", views.add_author, name="addAuthor"),

    # Your login/logout views
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('login/token/', views.login, name='login_url'),
    path('login/public/', views.public_key_view, name='public_key_view'),



]




