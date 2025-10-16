import os
from openai import OpenAI
from typing import Optional

# 初始化 OpenAI 客户端
client = OpenAI(
    base_url=os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
    api_key=os.environ.get("ARK_API_KEY"),
)

if not os.environ.get("ARK_API_KEY"):
    # Warn the operator; do not expose secrets in code
    print("WARNING: ARK_API_KEY environment variable is not set. AI requests will likely fail.")


def get_ai_response(system: str, user: str, model: str = "doubao-1-5-lite-32k-250115") -> Optional[str]:
    """Send a non-streaming chat completion request.

    Args:
        system: system prompt string
        user: user prompt string
        model: model id to call (default set to the provided model)

    Returns:
        The assistant text content, or None on error.
    """
    try:
        # Debug: print request params (do not print API key)
        print("[AI DEBUG] Sending request:\n  model:", model, "\n  system:\n", system, "\n  user:\n", user)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        print("[AI DEBUG] Received completion object")
        content = completion.choices[0].message.content
        print("[AI DEBUG] Completion content:\n", content)
        return content
    except Exception as e:
        # In real code consider logging
        print(f"AI request failed: {e}", flush=True)
        return None


def stream_ai_response(system: str, user: str, model: str = "doubao-1-5-lite-32k-250115"):
    """Return a generator that yields streaming chunks from the AI API.

    Yields chunk strings (may be partial). Caller should iterate and assemble if needed.
    """
    print("[AI DEBUG] Starting streaming request:\n  model:", model)
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        stream=True,
    )

    for chunk in stream:
        print("[AI DEBUG] Received stream chunk:", getattr(chunk, 'choices', None))
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        # delta may have .content for streaming partials
        content = getattr(delta, "content", None)
        if content:
            print("[AI DEBUG] Stream chunk content:", content)
            yield content
