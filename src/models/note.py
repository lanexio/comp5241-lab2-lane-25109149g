
from src.database.db import db

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Note {self.title}>'

