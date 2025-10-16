
from flask import Blueprint, request, jsonify
from src.models.note import Note
from src.database.db import db

note_bp = Blueprint("note_bp", __name__)

@note_bp.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    new_note = Note(title=title, content=content)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"message": "Note created successfully", "note": {"id": new_note.id, "title": new_note.title, "content": new_note.content, "timestamp": new_note.timestamp}}), 201

@note_bp.route("/notes", methods=["GET"])
def get_all_notes():
    notes = Note.query.order_by(Note.timestamp.desc()).all()
    output = []
    for note in notes:
        output.append({"id": note.id, "title": note.title, "content": note.content, "timestamp": note.timestamp})
    return jsonify({"notes": output})

@note_bp.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    return jsonify({"id": note.id, "title": note.title, "content": note.content, "timestamp": note.timestamp})

@note_bp.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)
    db.session.commit()
    return jsonify({"message": "Note updated successfully", "note": {"id": note.id, "title": note.title, "content": note.content, "timestamp": note.timestamp}})

@note_bp.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted successfully"})

@note_bp.route("/notes/search", methods=["GET"])
def search_notes():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"notes": []})
    
    search_results = Note.query.filter(
        (Note.title.ilike(f"%{query}%")) | (Note.content.ilike(f"%{query}%"))
    ).order_by(Note.timestamp.desc()).all()

    output = []
    for note in search_results:
        output.append({"id": note.id, "title": note.title, "content": note.content, "timestamp": note.timestamp})
    return jsonify({"notes": output})

