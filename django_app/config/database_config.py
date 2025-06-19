
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Database routers
DATABASE_ROUTERS = ['django_app.db_routers.FolderBasedRouter']

# Redis cache configuration
CACHES = {
    # Make Redis the default cache
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
    # "default": {
    #     "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
    #     "LOCATION": "127.0.0.1:11211",
    # }
    
}
