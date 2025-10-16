from asgiref.wsgi import WsgiToAsgi
import os
import sys

# Ensure src package is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT))

# Normalize DATABASE_URL early so that SQLAlchemy picks the psycopg2 driver
db_env = os.environ.get('DATABASE_URL') or os.environ.get('SUPABASE_DATABASE_URL')
if db_env:
	# common forms: postgres://, postgresql://, postgres+pg8000://, postgresql+pg8000://
	if db_env.startswith('postgres://'):
		db_env = db_env.replace('postgres://', 'postgresql+psycopg2://', 1)
	if '+pg8000' in db_env:
		db_env = db_env.replace('+pg8000', '+psycopg2')
	if db_env.startswith('postgresql://'):
		db_env = db_env.replace('postgresql://', 'postgresql+psycopg2://', 1)
	os.environ['DATABASE_URL'] = db_env

from src.main import app as flask_app

# Wrap Flask WSGI app as ASGI so Vercel's Python runtime can serve it
asgi_app = WsgiToAsgi(flask_app)

# Vercel expects the module-level variable to be named 'app' or 'asgi_app'
app = asgi_app
