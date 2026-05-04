import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'raqamli_markaz'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raqamli_markaz.settings')

app = get_wsgi_application()
application = app
