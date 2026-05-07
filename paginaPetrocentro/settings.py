import os 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# configuracion de estaticos 
STATIC_URL = '/static/'

STATICFILES_DIRS = [
  BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"
