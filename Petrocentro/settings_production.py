
import os
from Petrocentro.settings import BASE_DIR
DEBUG = False

ALLOWED_HOSTS = ['72.167.141.51','petrocentro.co', 'www.petrocentro.co' ]


DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'petrocentro',
        'USER': 'PTC-DB-01',
        'PASSWORD': 'Ti.wt.24.',
        'HOST': 'localhost',
        'PORT':'3306',
    }
}



STATIC_ROOT =   os.path.join(BASE_DIR,"staticfiles")

MEDIA_ROOT =   os.path.join(BASE_DIR,"media")