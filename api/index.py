from asgiref.wsgi import WsgiToAsgi
import os
import sys

# Ensure src package is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT))

from src.main import app as flask_app

# Wrap Flask WSGI app as ASGI so Vercel's Python runtime can serve it
asgi_app = WsgiToAsgi(flask_app)

# Vercel expects the module-level variable to be named 'app' or 'asgi_app'
app = asgi_app
