import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.database.db import db
from src.models.note import Note
from src.routes.note_routes import note_bp
from src.routes.ai_routes import ai_bp
import ssl

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.register_blueprint(note_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')


# 使用新的Supabase Transaction pooler连接信息
database_url = 'postgresql://postgres.lxatrvonizvxdzftswuj:XX19980519@aws-1-us-east-2.pooler.supabase.com:6543/postgres'



if 1 == 1:
    if database_url.startswith('postgresql://'):
        # 使用 pg8000 驱动
        database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)

# 配置SSL连接
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# 为 pg8000 配置 SSL
ssl_context = ssl.create_default_context()

ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'ssl_context': ssl_context
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False





# 安全的启动日志（隐藏凭据）
try:
    redacted = database_url.split('://', 1)[0] + '://REDACTED'
except Exception:
    redacted = 'unknown'
print(f"[startup] Using SQLALCHEMY_DATABASE_URI: {redacted}")

db.init_app(app)

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