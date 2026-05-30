#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Flask Backend
Proxies requests to Ckey.vn & Cocolink.ai, supports Chat & TTS
"""

import os, json
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='.')
CORS(app)

# ==================== PROVIDERS & MODELS ====================
PROVIDERS = {
    "ckey": {
        "name": "Ckey.vn",
        "api_key": os.environ.get("CKEY_API_KEY",
            "sk-e317a237354192e26f99951f06e4882779e8a0e08e86d2f71242e8ff770bdf24"),
        "base_url": "https://ckey.vn/v1/chat/completions",
        "tts_url": "https://ckey.vn/v1/audio/speech",
        "models": [
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
            {"name": "phuocanh421994/Qwen3.6 27b", "type": "text", "tier": "PAID", "desc": "Qwen3.6 27B"},
            {"name": "phuocanh421994/Qwen3.6 35b a3b", "type": "text", "tier": "PAID", "desc": "Qwen3.6 35B"},
            {"name": "phuocanh421994/Qwen3.6-Flash", "type": "text", "tier": "PAID", "desc": "Qwen3.6 Flash"},
            {"name": "phuocanh421994/Deepseek V4 Pro", "type": "text", "tier": "PAID", "desc": "Deepseek V4 Pro"},
            {"name": "phuocanh421994/Qwen 3.6 Max Preview", "type": "text", "tier": "PAID", "desc": "Qwen 3.6 Max"},
            {"name": "phuocanh421994/Qwen3.5 Plus", "type": "text", "tier": "PAID", "desc": "Qwen3.5 Plus"},
            {"name": "phuocanh421994/Qwen 3.6 Plus", "type": "text", "tier": "PAID", "desc": "Qwen 3.6 Plus"},
            {"name": "phuocanh421994/Qwen3 Max", "type": "text", "tier": "PAID", "desc": "Qwen3 Max"},
            {"name": "phuocanh421994/Qwen3 Coder Plus", "type": "text", "tier": "PAID", "desc": "Qwen3 Coder Plus"},
            {"name": "phuocanh421994/Qwen 3.7 max", "type": "text", "tier": "PAID", "desc": "Qwen 3.7 Max"},
            {"name": "vykelongthuong/Deepseek V4 Flash", "type": "text", "tier": "PAID", "desc": "Deepseek V4 Flash"},
            {"name": "hiennqhust/qwen3.6-27b", "type": "text", "tier": "PAID", "desc": "Qwen3.6 27B HUST"},
            {"name": "hiennqhust/gpt-5.4", "type": "text", "tier": "PAID", "desc": "GPT 5.4 HUST"},
            {"name": "hiennqhust/deepseek-v4-flash", "type": "text", "tier": "PAID", "desc": "DeepSeek V4 Flash HUST"},
            {"name": "claude-sonnet-4.5", "type": "text", "tier": "PAID", "desc": "Claude Sonnet 4.5"},
            {"name": "deepseek-v4-pro", "type": "text", "tier": "PAID", "desc": "DeepSeek V4 Pro"},
            # TTS models
            {"name": "vi-VN-NamMinhNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nam", "voice": "NamMinh"},
            {"name": "vi-VN-HoaiMyNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nữ", "voice": "HoaiMy"},
            {"name": "google-tts/vi", "type": "tts", "tier": "FREE", "desc": "Google TTS", "voice": "alloy"},
        ]
    },
    "cocolink": {
        "name": "Cocolink.ai",
        "api_key": os.environ.get("COCOLINK_API_KEY",
            "sk-fAC9npWdz1ynogX_Ppt0Xdi44Sm_aIIXLrJRE1AAoIyelVGvMl4KXGdgn3U"),
        "base_url": "https://www.cocolink.ai/v1/chat/completions",
        "tts_url": None,
        "models": [
            {"name": "qwen-plus", "type": "text", "tier": "PAID", "desc": "Qwen Plus"},
            {"name": "qwen-turbo", "type": "text", "tier": "PAID", "desc": "Qwen Turbo"},
            {"name": "qwen3-coder-flash", "type": "text", "tier": "PAID", "desc": "Qwen3 Coder Flash"},
            {"name": "qwen3.5-flash", "type": "text", "tier": "PAID", "desc": "Qwen 3.5 Flash"},
        ]
    }
}

# Flatten all models with id, type, etc.
ALL_MODELS = []
for pkey, pdata in PROVIDERS.items():
    for m in pdata["models"]:
        ALL_MODELS.append({
            "id": f"{pkey}:{m['name']}",
            "name": m["name"],
            "provider": pkey,
            "provider_name": pdata["name"],
            "type": m.get("type", "text"),
            "tier": m["tier"],
            "desc": m["desc"],
            "voice": m.get("voice", "")
        })

# ==================== ROUTES ====================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/models')
def get_models():
    return jsonify({"models": ALL_MODELS})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    model_id = data.get("model", "")
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Parse provider:model_name
    if ":" in model_id:
        provider_key, model_name = model_id.split(":", 1)
    else:
        provider_key = "ckey"
        model_name = model_id

    if provider_key not in PROVIDERS:
        return jsonify({"error": f"Unknown provider: {provider_key}"}), 400

    provider = PROVIDERS[provider_key]
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7,
        "max_tokens": 2048
    }

    try:
        resp = requests.post(provider["base_url"], headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            return jsonify({"error": f"API error: {resp.status_code}"}), 502
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
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    model_id = data.get("model", "ckey:vi-VN-NamMinhNeural")
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Determine voice from model
    voice = "NamMinh"  # default
    for m in ALL_MODELS:
        if m["id"] == model_id and m["type"] == "tts":
            voice = m.get("voice", "NamMinh")
            break

    provider_key = "ckey"  # Only ckey supports TTS currently
    provider = PROVIDERS[provider_key]
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id.split(":")[-1],  # take only model name
        "input": text,
        "voice": voice
    }

    try:
        resp = requests.post(provider["tts_url"], headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            return jsonify({"error": f"TTS API error: {resp.status_code}"}), 502
        return Response(resp.content, mimetype="audio/mpeg",
                        headers={"Content-Disposition": "attachment; filename=speech.mp3"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
