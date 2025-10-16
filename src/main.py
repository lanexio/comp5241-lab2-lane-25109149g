
import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.database.db import db
from src.models.note import Note
from src.routes.note_routes import note_bp
from src.routes.ai_routes import ai_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.register_blueprint(note_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')

# uncomment if you need to use database
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
# Allow overriding DB via DATABASE_URL (e.g. Supabase/Postgres). If DATABASE_URL uses the old 'postgres://' prefix,
# SQLAlchemy prefers 'postgresql://'. Normalize if necessary.
database_url = os.environ.get('DATABASE_URL') or os.environ.get('SUPABASE_DATABASE_URL')
if database_url:
    # Normalize old-style postgres:// to use the pg8000 driver which is pure-Python
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
    else:
        # If the URL already contains a driver, keep it. If it is 'postgresql://', prefer pg8000 transport
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
    # Ensure Note table is created
    Note.__table__.create(db.engine, checkfirst=True)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

