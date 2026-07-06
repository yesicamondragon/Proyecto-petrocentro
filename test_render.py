import os
import sys
import django

# Add project root to sys.path
sys.path.append(r'c:\Users\Administrador\Proyecto-petrocentro')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Petrocentro.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from users.views import gestion_inventario
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage

User = get_user_model()
factory = RequestFactory()

users = User.objects.all()
print(f"Total users to test: {users.count()}")

for user in users:
    request = factory.get('/inventario/')
    request.user = user

    # Add session middleware support
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    # Add messages support
    setattr(request, '_messages', FallbackStorage(request))

    try:
        response = gestion_inventario(request)
        print(f"User: {user} ({user.rol if hasattr(user, 'rol') else 'N/A'}) - STATUS CODE: {response.status_code}")
    except Exception as e:
        print(f"User: {user} ({user.rol if hasattr(user, 'rol') else 'N/A'}) - FAILED!")
        import traceback
        traceback.print_exc()
        # Keep looping to see if others fail too
