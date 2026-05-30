#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Flask Backend
Proxies requests to Ckey.vn & Cocolink.ai with all models
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
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
        "models": [
            {"name": "chieustudio/deepseek-r1", "tier": "FREE", "desc": "DeepSeek R1"},
            {"name": "mistral-medium-3.5-128b", "tier": "FREE", "desc": "Mistral Medium 3.5"},
            {"name": "glm4.7", "tier": "FREE", "desc": "GLM 4.7"},
            {"name": "qwen3-coder-480b-a35b-instruct", "tier": "FREE", "desc": "Qwen3 Coder 480B"},
            {"name": "mistral-small-4-119b-2603", "tier": "FREE", "desc": "Mistral Small 4"},
            {"name": "chieustudio/mistral-large-3-675b-instruct-2512", "tier": "FREE", "desc": "Mistral Large 3 675B"},
            {"name": "deepseek-r1-distill-qwen-32b", "tier": "PAID", "desc": "DeepSeek R1 Distill"},
            {"name": "deepseek-3.2", "tier": "PAID", "desc": "DeepSeek 3.2"},
            {"name": "qwen3-coder-next", "tier": "PAID", "desc": "Qwen3 Coder Next"},
            {"name": "minimax-m2.5", "tier": "PAID", "desc": "Minimax M2.5"},
            {"name": "minimax-m2.1", "tier": "PAID", "desc": "Minimax M2.1"},
            {"name": "mistral-large-3-675b-instruct-2512", "tier": "PAID", "desc": "Mistral Large 3 675B"},
            {"name": "deepseek-v4-flash", "tier": "PAID", "desc": "DeepSeek V4 Flash"},
            {"name": "kimi-k2.5", "tier": "PAID", "desc": "Kimi K2.5"},
            {"name": "gpt-5.4-mini", "tier": "PAID", "desc": "GPT 5.4 Mini"},
            {"name": "gpt-5.2", "tier": "PAID", "desc": "GPT 5.2"},
            {"name": "gpt-5.3-codex", "tier": "PAID", "desc": "GPT 5.3 Codex"},
            {"name": "gpt-5.4", "tier": "PAID", "desc": "GPT 5.4"},
            {"name": "gpt-5.5", "tier": "PAID", "desc": "GPT 5.5"},
            {"name": "claude-haiku-4.5", "tier": "PAID", "desc": "Claude Haiku 4.5"},
            {"name": "claude-sonnet-4.6", "tier": "PAID", "desc": "Claude Sonnet 4.6"},
            {"name": "claude-opus-4.6", "tier": "PAID", "desc": "Claude Opus 4.6"},
            {"name": "glm-5", "tier": "PAID", "desc": "GLM-5"},
            {"name": "glm-5.1", "tier": "PAID", "desc": "GLM-5.1"},
            {"name": "kimi-k2.6", "tier": "PAID", "desc": "Kimi K2.6"},
            {"name": "phuocanh421994/Qwen3.6 27b", "tier": "PAID", "desc": "Qwen3.6 27B"},
            {"name": "phuocanh421994/Qwen3.6 35b a3b", "tier": "PAID", "desc": "Qwen3.6 35B"},
            {"name": "phuocanh421994/Qwen3.6-Flash", "tier": "PAID", "desc": "Qwen3.6 Flash"},
            {"name": "phuocanh421994/Deepseek V4 Pro", "tier": "PAID", "desc": "Deepseek V4 Pro"},
            {"name": "phuocanh421994/Qwen 3.6 Max Preview", "tier": "PAID", "desc": "Qwen 3.6 Max"},
            {"name": "phuocanh421994/Qwen3.5 Plus", "tier": "PAID", "desc": "Qwen3.5 Plus"},
            {"name": "phuocanh421994/Qwen 3.6 Plus", "tier": "PAID", "desc": "Qwen 3.6 Plus"},
            {"name": "phuocanh421994/Qwen3 Max", "tier": "PAID", "desc": "Qwen3 Max"},
            {"name": "phuocanh421994/Qwen3 Coder Plus", "tier": "PAID", "desc": "Qwen3 Coder Plus"},
            {"name": "phuocanh421994/Qwen 3.7 max", "tier": "PAID", "desc": "Qwen 3.7 Max"},
            {"name": "vykelongthuong/Deepseek V4 Flash", "tier": "PAID", "desc": "Deepseek V4 Flash"},
            {"name": "hiennqhust/qwen3.6-27b", "tier": "PAID", "desc": "Qwen3.6 27B HUST"},
            {"name": "hiennqhust/gpt-5.4", "tier": "PAID", "desc": "GPT 5.4 HUST"},
            {"name": "hiennqhust/deepseek-v4-flash", "tier": "PAID", "desc": "DeepSeek V4 Flash HUST"},
            {"name": "claude-sonnet-4.5", "tier": "PAID", "desc": "Claude Sonnet 4.5"},
            {"name": "deepseek-v4-pro", "tier": "PAID", "desc": "DeepSeek V4 Pro"},
            {"name": "phuocanh421994/Qwen 3.7 max", "tier": "PAID", "desc": "Qwen 3.7 Max"},
        ]
    },
    "cocolink": {
        "name": "Cocolink.ai",
        "api_key": os.environ.get("COCOLINK_API_KEY",
            "sk-fAC9npWdz1ynogX_Ppt0Xdi44Sm_aIIXLrJRE1AAoIyelVGvMl4KXGdgn3U"),
        "base_url": "https://www.cocolink.ai/v1/chat/completions",
        "models": [
            {"name": "qwen-plus", "tier": "PAID", "desc": "Qwen Plus"},
            {"name": "qwen-turbo", "tier": "PAID", "desc": "Qwen Turbo"},
            {"name": "qwen3-coder-flash", "tier": "PAID", "desc": "Qwen3 Coder Flash"},
            {"name": "qwen3.5-flash", "tier": "PAID", "desc": "Qwen 3.5 Flash"},
        ]
    }
}

# Flatten all models
ALL_MODELS = []
for pkey, pdata in PROVIDERS.items():
    for m in pdata["models"]:
        ALL_MODELS.append({
            "id": f"{pkey}:{m['name']}",
            "name": m["name"],
            "provider": pkey,
            "provider_name": pdata["name"],
            "tier": m["tier"],
            "desc": m["desc"]
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
