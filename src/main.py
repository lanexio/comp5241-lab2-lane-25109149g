import os
import sys
# DON'T CHANGE THIS !!!
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


# 使用新的Supabase Transaction pooler连接信息
database_url = 'postgresql://postgres.lxatrvonizvxdzftswuj:XX19980519@aws-1-us-east-2.pooler.supabase.com:6543/postgres'

# 标准化：在 Vercel 上使用纯 Python 的 pg8000 驱动以避免二进制轮子构建问题，本地开发默认使用 psycopg2
if 1==1:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    if '+pg8000' in database_url:
        database_url = database_url.replace('+pg8000', '+psycopg2')
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

# 配置SSL连接（关键，因为Transaction pooler通常需要SSL）
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'sslmode': 'require'
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