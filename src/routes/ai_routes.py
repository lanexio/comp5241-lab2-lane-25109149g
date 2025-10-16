from flask import Blueprint, request, jsonify
import json
from src.ai_client import get_ai_response
from flask import current_app

ai_bp = Blueprint("ai_bp", __name__)


@ai_bp.route("/translate", methods=["POST"])
def translate():
    """Translate provided texts to English using the AI client.

    Expects JSON: { items: [ {id: <string>, text: <string>}, ... ] }
    Returns: { translations: [<string>, ...] }
    """
    payload = request.get_json(silent=True)
    if not payload or "items" not in payload:
        return jsonify({"error": "Missing items in request"}), 400

    items = payload.get("items")
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400

    # Build a user prompt listing items in order and ask for a JSON array of translations
    user_lines = [f"{idx+1}. {it.get('text','')}" for idx, it in enumerate(items)]
    expected_count = len(items)
    user_prompt = (
        "Translate the following texts. For each item: if the original text appears to be English, translate it to Chinese; otherwise translate it to English.\n"
        "Return ONLY a JSON array (no extra text) where each element is the translation string corresponding to the input order.\n"
        f"Return exactly {expected_count} elements in the array.\n\n"
        "Inputs:\n"
        + "\n".join(user_lines)
    )

    system_prompt = (
        "You are a helpful translator.\n"
        "Make concise, natural translations and preserve meaning.\n"
        "For each input: if the original text appears to be English, translate it to Chinese; otherwise translate it to English.\n"
        "Output must be a valid JSON array of strings only (no extra text)."
    )

    ai_response = get_ai_response(system_prompt, user_prompt)
    if ai_response is None:
        return jsonify({"error": "AI translation failed", "user_prompt": user_prompt}), 500

    # Try to parse AI response as JSON; if parsing fails, return raw text with error
    try:
        parsed = json.loads(ai_response)
        if not isinstance(parsed, list):
            raise ValueError("Parsed JSON is not a list")

        # Align parsed results to expected count: trim extras or pad with empty strings
        aligned = True
        if len(parsed) > expected_count:
            parsed = parsed[:expected_count]
            aligned = False
        elif len(parsed) < expected_count:
            parsed = parsed + [""] * (expected_count - len(parsed))
            aligned = False

        # Include AI raw response and prompt for debugging
        return jsonify({
            "translations": parsed,
            "ai_raw": ai_response,
            "user_prompt": user_prompt,
            "aligned": aligned,
            "expected_count": expected_count,
            "returned_count": len(json.loads(ai_response)) if isinstance(json.loads(ai_response), list) else None,
        })
    except Exception:
        # fallback: return the raw AI response so client can inspect
        return jsonify({"error": "Failed to parse AI response as JSON", "raw": ai_response, "user_prompt": user_prompt}), 500


@ai_bp.route("/generate_note", methods=["POST"])
def generate_note():
    """Generate a note title, content and tags from a natural language description.

    Request JSON: { description: str, language: str }
    Response JSON: { title: str, content: str, tags: [str, ...], ai_raw: str }
    """
    payload = request.get_json(silent=True)
    if not payload or "description" not in payload:
        return jsonify({"error": "Missing description"}), 400

    description = payload.get("description", "")
    language = payload.get("language", "English")

    # Build prompt: ask AI to produce JSON with title, content and three tags
    user_prompt = (
        f"You are a helpful assistant that generates a structured note.\n"
        f"Generate a concise title, a short paragraph content, and three suggested tags (keywords).\n"
        f"Output must be a JSON object: {{\"title\": string, \"content\": string, \"tags\": [string,string,string]}} and nothing else.\n"
        f"The requested output language is: {language}.\n"
        f"User description: {description}"
    )

    system_prompt = (
        "You are a note-generation assistant. Be concise and produce user-ready content.\n"
        "Preserve meaning from the description. Output only valid JSON as specified."
    )

    ai_response = get_ai_response(system_prompt, user_prompt)
    if ai_response is None:
        return jsonify({"error": "AI generation failed"}), 500

    try:
        parsed = json.loads(ai_response)
        title = parsed.get("title", "") if isinstance(parsed, dict) else ""
        content = parsed.get("content", "") if isinstance(parsed, dict) else ""
        tags = parsed.get("tags", []) if isinstance(parsed, dict) else []
        # normalize tags to array of strings and take up to 3
        if not isinstance(tags, list):
            tags = []
        tags = [str(t) for t in tags][:3]

        return jsonify({"title": title, "content": content, "tags": tags, "ai_raw": ai_response})
    except Exception:
        # try to be forgiving: return raw ai text
        return jsonify({"error": "Failed to parse AI response as JSON", "raw": ai_response}), 500
