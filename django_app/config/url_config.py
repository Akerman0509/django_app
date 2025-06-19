


ROOT_URLCONF = 'django_app.urls'
STATIC_URL = 'static/'
# URLs for login/logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/my_app/authors/' # need first /
LOGOUT_REDIRECT_URL = '/my_app/login/'
