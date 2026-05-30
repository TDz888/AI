#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Flask Backend v3.0
Hỗ trợ streaming (Server-Sent Events), API key động, lỗi rõ ràng.
"""

import os, json
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='.')
CORS(app)

# Cấu hình
DEFAULT_API_KEY = os.environ.get("API_KEY",
    "sk-e317a237354192e26f99951f06e4882779e8a0e08e86d2f71242e8ff770bdf24")
BASE_URL = "https://ckey.vn/v1/chat/completions"
TTS_URL = "https://ckey.vn/v1/audio/speech"

MODELS = [
    # Text models
    {"name": "chieustudio/deepseek-r1", "type": "text", "tier": "FREE", "desc": "DeepSeek R1"},
    {"name": "mistral-medium-3.5-128b", "type": "text", "tier": "FREE", "desc": "Mistral Medium 3.5"},
    {"name": "glm4.7", "type": "text", "tier": "FREE", "desc": "GLM 4.7"},
    {"name": "qwen3-coder-480b-a35b-instruct", "type": "text", "tier": "FREE", "desc": "Qwen3 Coder 480B"},
    {"name": "mistral-small-4-119b-2603", "type": "text", "tier": "FREE", "desc": "Mistral Small 4"},
    {"name": "chieustudio/mistral-large-3-675b-instruct-2512", "type": "text", "tier": "FREE", "desc": "Mistral Large 3 675B"},
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
    # TTS models
    {"name": "vi-VN-NamMinhNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nam", "voice": "NamMinh"},
    {"name": "vi-VN-HoaiMyNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nữ", "voice": "HoaiMy"},
    {"name": "google-tts/vi", "type": "tts", "tier": "FREE", "desc": "Google TTS", "voice": "alloy"},
]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/models')
def get_models():
    return jsonify(MODELS)

def error_response(status, message):
    response = jsonify({"error": message})
    response.status_code = status
    return response

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return error_response(400, "Dữ liệu JSON không hợp lệ")

    api_key = data.get("api_key") or DEFAULT_API_KEY
    model = data.get("model", "chieustudio/deepseek-r1")
    message = data.get("message", "")
    stream = data.get("stream", False)  # Cho phép client yêu cầu streaming

    if not message:
        return error_response(400, "Thiếu nội dung tin nhắn")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "max_tokens": 2048,
        "stream": stream
    }

    if stream:
        def generate():
            try:
                resp = requests.post(BASE_URL, headers=headers, json=payload, stream=True, timeout=120)
                if resp.status_code != 200:
                    yield f"data: {json.dumps({'error': f'API lỗi {resp.status_code}'})}\n\n"
                    return
                for line in resp.iter_lines(decode_unicode=True):
                    if line and line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    # Gửi nội dung từng token
                                    yield f"data: {json.dumps({'token': content})}\n\n"
                            # Có thể gửi usage ở chunk cuối
                        except json.JSONDecodeError:
                            pass
                yield "data: [DONE]\n\n"
            except requests.exceptions.Timeout:
                yield f"data: {json.dumps({'error': 'Yêu cầu quá thời gian'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    else:
        try:
            resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
            if resp.status_code != 200:
                try:
                    err = resp.json()
                except:
                    err = resp.text
                return error_response(resp.status_code, f"API lỗi: {err}")
            result = resp.json()
            ai_response = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            return jsonify({
                "response": ai_response,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            })
        except requests.exceptions.Timeout:
            return error_response(504, "Yêu cầu quá thời gian")
        except Exception as e:
            return error_response(500, str(e))

@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json(force=True)
    except:
        return error_response(400, "Dữ liệu JSON không hợp lệ")

    api_key = data.get("api_key") or DEFAULT_API_KEY
    model = data.get("model", "vi-VN-NamMinhNeural")
    text = data.get("text", "")
    if not text:
        return error_response(400, "Thiếu văn bản")

    voice = "NamMinh"
    for m in MODELS:
        if m["name"] == model and m["type"] == "tts":
            voice = m.get("voice", "NamMinh")
            break

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "input": text,
        "voice": voice
    }

    try:
        resp = requests.post(TTS_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            try:
                err = resp.json()
            except:
                err = resp.text
            return error_response(resp.status_code, f"TTS lỗi: {err}")
        return Response(resp.content, mimetype="audio/mpeg",
                        headers={"Content-Disposition": "attachment; filename=speech.mp3"})
    except Exception as e:
        return error_response(500, str(e))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server ready at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
