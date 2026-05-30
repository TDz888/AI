#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Flask Backend (Production Ready)
- Keep‑alive ping trong SSE để tránh 502
- Hỗ trợ multi‑turn messages
- Tích hợp TTS
"""

import os, json, time, logging
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ───── Logging ─────
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ───── Config ─────
DEFAULT_API_KEY = os.environ.get("API_KEY", "sk-e317a237354192e26f99951f06e4882779e8a0e08e86d2f71242e8ff770bdf24")
BASE_URL = os.environ.get("BASE_URL", "https://ckey.vn/v1/chat/completions")
TTS_URL  = os.environ.get("TTS_URL", "https://ckey.vn/v1/audio/speech")

# ───── HTTP Session với retry ─────
retry_strategy = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=50, pool_maxsize=100)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# ───── Models ─────
MODELS = [
    # Text FREE
    {"name": "chieustudio/deepseek-r1", "type": "text", "tier": "FREE", "desc": "DeepSeek R1"},
    {"name": "mistral-medium-3.5-128b", "type": "text", "tier": "FREE", "desc": "Mistral Medium 3.5"},
    {"name": "glm4.7", "type": "text", "tier": "FREE", "desc": "GLM 4.7"},
    {"name": "qwen3-coder-480b-a35b-instruct", "type": "text", "tier": "FREE", "desc": "Qwen3 Coder 480B"},
    {"name": "mistral-small-4-119b-2603", "type": "text", "tier": "FREE", "desc": "Mistral Small 4"},
    {"name": "chieustudio/mistral-large-3-675b-instruct-2512", "type": "text", "tier": "FREE", "desc": "Mistral Large 3 675B"},
    # Text PAID
    {"name": "deepseek-r1-distill-qwen-32b", "type": "text", "tier": "PAID", "desc": "DeepSeek R1 Distill"},
    {"name": "deepseek-3.2", "type": "text", "tier": "PAID", "desc": "DeepSeek 3.2"},
    {"name": "qwen3-coder-next", "type": "text", "tier": "PAID", "desc": "Qwen3 Coder Next"},
    {"name": "minimax-m2.5", "type": "text", "tier": "PAID", "desc": "Minimax M2.5"},
    {"name": "minimax-m2.1", "type": "text", "tier": "PAID", "desc": "Minimax M2.1"},
    {"name": "mistral-large-3-675b-instruct-2512", "type": "text", "tier": "PAID", "desc": "Mistral Large 3 675B"},
    {"name": "deepseek-v4-flash", "type": "text", "tier": "PAID", "desc": "DeepSeek V4 Flash"},
    {"name": "kimi-k2.5", "type": "text", "tier": "PAID", "desc": "Kimi K2.5"},
    {"name": "gpt-5.4-mini", "type": "text", "tier": "PAID", "desc": "GPT 5.4 Mini"},
    {"name": "gpt-5.2", "type": "text", "tier": "PAID", "desc": "GPT 5.2"},
    {"name": "gpt-5.3-codex", "type": "text", "tier": "PAID", "desc": "GPT 5.3 Codex"},
    {"name": "gpt-5.4", "type": "text", "tier": "PAID", "desc": "GPT 5.4"},
    {"name": "gpt-5.5", "type": "text", "tier": "PAID", "desc": "GPT 5.5"},
    {"name": "claude-haiku-4.5", "type": "text", "tier": "PAID", "desc": "Claude Haiku 4.5"},
    {"name": "claude-sonnet-4.6", "type": "text", "tier": "PAID", "desc": "Claude Sonnet 4.6"},
    {"name": "claude-opus-4.6", "type": "text", "tier": "PAID", "desc": "Claude Opus 4.6"},
    {"name": "glm-5", "type": "text", "tier": "PAID", "desc": "GLM-5"},
    {"name": "glm-5.1", "type": "text", "tier": "PAID", "desc": "GLM-5.1"},
    {"name": "kimi-k2.6", "type": "text", "tier": "PAID", "desc": "Kimi K2.6"},
    # TTS FREE
    {"name": "vi-VN-NamMinhNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nam VN", "voice": "NamMinh"},
    {"name": "vi-VN-HoaiMyNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nữ VN", "voice": "HoaiMy"},
    {"name": "google-tts/vi", "type": "tts", "tier": "FREE", "desc": "Google TTS", "voice": "alloy"},
]

# ───── Routes ─────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/models')
def get_models():
    return jsonify(MODELS)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    api_key = data.get("api_key") or DEFAULT_API_KEY
    model = data.get("model", "chieustudio/deepseek-r1")
    stream = data.get("stream", False)
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 4096)

    # Hỗ trợ cả message đơn lẻ và messages (multi‑turn)
    messages = data.get("messages")
    if not messages:
        msg = data.get("message", "")
        if msg:
            messages = [{"role": "user", "content": msg}]
        else:
            return jsonify({"error": {"message": "No message provided"}}), 400

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "stream": stream}

    if stream:
        def generate():
            try:
                resp = http.post(BASE_URL, headers=headers, json=payload, stream=True, timeout=(10, 300))
                if resp.status_code != 200:
                    yield f"data: {json.dumps({'error': f'API error {resp.status_code}'})}\n\n"
                    return
                last_ping = time.time()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                reasoning = delta.get("reasoning_content", "") or delta.get("reasoning", "")
                                out = {}
                                if content: out["token"] = content
                                if reasoning: out["thinking"] = reasoning
                                if out:
                                    yield f"data: {json.dumps(out, ensure_ascii=False)}\n\n"
                        except json.JSONDecodeError:
                            pass
                    # 🔥 Keep‑alive mỗi 15 giây để tránh tunnel timeout
                    if time.time() - last_ping > 15:
                        yield ": keepalive\n\n"
                        last_ping = time.time()
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    else:
        try:
            resp = http.post(BASE_URL, headers=headers, json=payload, timeout=300)
            if resp.status_code != 200:
                return jsonify({"error": {"message": f"API error {resp.status_code}"}}), resp.status_code
            result = resp.json()
            ai_resp = result["choices"][0]["message"]["content"]
            reasoning = result["choices"][0]["message"].get("reasoning_content", "")
            usage = result.get("usage", {})
            return jsonify({"response": ai_resp, "thinking": reasoning, "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }})
        except Exception as e:
            return jsonify({"error": {"message": str(e)}}), 500

@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.get_json(force=True, silent=True) or {}
    api_key = data.get("api_key") or DEFAULT_API_KEY
    model = data.get("model", "vi-VN-NamMinhNeural")
    text = data.get("text", "")
    if not text:
        return jsonify({"error": {"message": "No text provided"}}), 400

    voice = "NamMinh"
    for m in MODELS:
        if m["name"] == model and m["type"] == "tts":
            voice = m.get("voice", "NamMinh")
            break

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "input": text, "voice": voice}

    try:
        resp = http.post(TTS_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            return jsonify({"error": {"message": f"TTS error {resp.status_code}"}}), resp.status_code
        return Response(resp.content, mimetype="audio/mpeg",
                        headers={"Content-Disposition": "attachment; filename=speech.mp3"})
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
