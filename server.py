#!/usr/bin/env python3
"""
🚀 Ultimate AI Chat Web – Flask Backend v4.0 (Production-Ready)
============================================================
Đặc điểm vượt trội:
- Hỗ trợ Streaming hoàn hảo (SSE) với nội dung suy nghĩ (DeepSeek R1 reasoning_content).
- Hỗ trợ gửi mảng messages (Multi-turn Chat) để lưu nhớ ngữ cảnh cuộc gọi.
- Quản lý kết nối thông minh (Connection Pool & Retries).
- Bảo mật thông tin, hạn chế tối đa rò rỉ API Key trong logs.
- Kháng lỗi tuyệt đối (Error Resilience).
"""

import os
import json
import logging
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS

# --- CẤU HÌNH LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Cho phép kết nối rộng rãi, an toàn

# --- CẤU HÌNH HỆ THỐNG ---
DEFAULT_API_KEY = os.environ.get("API_KEY", "sk-e317a237354192e26f99951f06e4882779e8a0e08e86d2f71242e8ff770bdf24")
BASE_URL = os.environ.get("BASE_URL", "https://ckey.vn/v1/chat/completions")
TTS_URL = os.environ.get("TTS_URL", "https://ckey.vn/v1/audio/speech")

# --- QUẢN LÝ KẾT NỐI (CONNECTION POOLING & RETRIES) ---
# Tối ưu hóa hiệu năng kết nối, tự động thử lại nếu gặp lỗi mạng tạm thời
http_session = requests.Session()
retries = Retry(
    total=3,                # Thử lại tối đa 3 lần
    backoff_factor=0.5,     # Thời gian chờ tăng dần giữa các lần thử (0.5s, 1s, 1.5s)
    status_forcelist=[500, 502, 503, 504], # Các mã lỗi server cần thử lại
    raise_on_status=False
)
http_session.mount("https://", HTTPAdapter(max_retries=retries, pool_connections=50, pool_maxsize=100))
http_session.mount("http://", HTTPAdapter(max_retries=retries, pool_connections=50, pool_maxsize=100))

# --- DANH SÁCH MODEL ---
MODELS = [
    # Text models (FREE & PAID)
    {"name": "chieustudio/deepseek-r1", "type": "text", "tier": "FREE", "desc": "DeepSeek R1 (Bản miễn phí chất lượng cao)"},
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
    {"name": "vi-VN-NamMinhNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nam Việt Nam", "voice": "NamMinh"},
    {"name": "vi-VN-HoaiMyNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nữ Việt Nam", "voice": "HoaiMy"},
    {"name": "google-tts/vi", "type": "tts", "tier": "FREE", "desc": "Google TTS Tiếng Việt", "voice": "alloy"},
]

def mask_key(key: str) -> str:
    """Mã hoá hiển thị API Key trong logs nhằm bảo mật"""
    if not key: return "N/A"
    if len(key) <= 12: return "***"
    return f"{key[:6]}...{key[-4:]}"

def create_error_response(status_code, message):
    """Tạo JSON response lỗi chuẩn nhất"""
    logger.error(f"API Error [{status_code}]: {message}")
    return jsonify({
        "error": {
            "message": message,
            "status": status_code,
            "type": "invalid_request_error"
        }
    }), status_code

# --- ROUTES ---

@app.route('/')
def index():
    """Phục vụ file frontend tĩnh từ thư mục gốc"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"Không tìm thấy index.html: {str(e)}")
        return "Frontend file 'index.html' not found in root directory.", 404

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra sức khoẻ của Server (Cho DevOps/Deployment monitoring)"""
    return jsonify({"status": "healthy", "service": "Ultimate AI Chat API", "version": "4.0"}), 200

@app.route('/api/models', methods=['GET'])
def get_models():
    """Trả về danh sách các model được hỗ trợ"""
    return jsonify(MODELS)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return create_error_response(400, "Dữ liệu JSON đầu vào không hợp lệ")

    # Thu thập cấu hình đầu vào
    api_key = data.get("api_key") or DEFAULT_API_KEY
    model = data.get("model", "chieustudio/deepseek-r1")
    stream = data.get("stream", False)
    temperature = data.get("temperature", 0.6)
    max_tokens = data.get("max_tokens", 4096)

    # Hỗ trợ cả hai cách gửi: một tin nhắn đơn 'message' hoặc chuỗi ngữ cảnh 'messages' (Multi-turn)
    raw_message = data.get("message")
    messages = data.get("messages")

    if not messages:
        if raw_message:
            messages = [{"role": "user", "content": raw_message}]
        else:
            return create_error_response(400, "Yêu cầu của bạn trống. Vui lòng cung cấp trường 'message' hoặc 'messages'.")

    # Log thông tin request an toàn
    logger.info(f"Yêu cầu Chat | Model: {model} | Stream: {stream} | API Key: {mask_key(api_key)}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Payload gửi lên API thượng nguồn
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }

    # Trường hợp STREAMING (SSE)
    if stream:
        def generate():
            try:
                # Đặt timeout hợp lý (Ví dụ: 10 giây để nhận byte đầu tiên, 120s tổng thời gian stream)
                resp = http_session.post(BASE_URL, headers=headers, json=payload, stream=True, timeout=(10, 120))
                
                if resp.status_code != 200:
                    err_text = resp.text
                    logger.error(f"Upstream API trả về lỗi: {resp.status_code} - {err_text}")
                    yield f"data: {json.dumps({'error': f'Lỗi API hệ thống ({resp.status_code})'})}\n\n"
                    return

                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                
                                # Hỗ trợ tối ưu cho DeepSeek R1 (Lấy cả phần content lẫn reasoning_content)
                                content = delta.get("content", "")
                                reasoning = delta.get("reasoning_content", "") or delta.get("reasoning", "")

                                # Đóng gói trả về frontend dưới cấu trúc chuẩn hóa siêu sạch
                                out_data = {}
                                if content:
                                    out_data["token"] = content
                                if reasoning:
                                    out_data["thinking"] = reasoning
                                
                                if out_data:
                                    yield f"data: {json.dumps(out_data, ensure_ascii=False)}\n\n"
                        except json.JSONDecodeError:
                            continue
                
                # Báo hiệu dòng dữ liệu đã kết thúc an toàn
                yield "data: [DONE]\n\n"

            except requests.exceptions.Timeout:
                logger.error("Kết nối đến Upstream API bị timeout.")
                yield f"data: {json.dumps({'error': 'Yêu cầu kết nối quá hạn (Timeout)'})}\n\n"
            except Exception as e:
                logger.error(f"Lỗi trong quá trình stream: {str(e)}")
                yield f"data: {json.dumps({'error': f'Lỗi luồng: {str(e)}'})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    # Trường hợp KHÔNG STREAM (Trả về một lần duy nhất)
    else:
        try:
            resp = http_session.post(BASE_URL, headers=headers, json=payload, timeout=90)
            if resp.status_code != 200:
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("error", {}).get("message", resp.text)
                except Exception:
                    err_msg = resp.text
                return create_error_response(resp.status_code, f"Lỗi API hệ thống: {err_msg}")

            result = resp.json()
            if "choices" not in result or len(result["choices"]) == 0:
                return create_error_response(502, "API trả về định dạng không đúng (thiếu choices)")

            choice = result["choices"][0]
            ai_response = choice.get("message", {}).get("content", "")
            reasoning_response = choice.get("message", {}).get("reasoning_content", "") or choice.get("message", {}).get("reasoning", "")
            
            usage = result.get("usage", {})

            # Trả về trọn vẹn kết quả cho frontend hiển thị
            return jsonify({
                "response": ai_response,
                "thinking": reasoning_response,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            })

        except requests.exceptions.Timeout:
            return create_error_response(504, "Upstream API quá thời gian phản hồi (Timeout)")
        except Exception as e:
            return create_error_response(500, f"Lỗi máy chủ nội bộ: {str(e)}")

@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return create_error_response(400, "Dữ liệu JSON đầu vào không hợp lệ")

    api_key = data.get("api_key") or DEFAULT_API_KEY
    model = data.get("model", "vi-VN-NamMinhNeural")
    text = data.get("text", "")

    if not text:
        return create_error_response(400, "Văn bản phát âm không được để trống")

    # Xác thực voice tương ứng với model đã chọn
    voice = "NamMinh"
    for m in MODELS:
        if m["name"] == model and m["type"] == "tts":
            voice = m.get("voice", "NamMinh")
            break

    logger.info(f"Yêu cầu TTS | Model: {model} | Voice: {voice} | Độ dài: {len(text)} ký tự")

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
        resp = http_session.post(TTS_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            try:
                err_text = resp.json()
            except Exception:
                err_text = resp.text
            return create_error_response(resp.status_code, f"Lỗi TTS: {err_text}")

        # Stream file âm thanh nhị phân (audio/mpeg) về trực tiếp cho trình duyệt phát
        return Response(
            resp.content,
            mimetype="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "no-cache"
            }
        )
    except requests.exceptions.Timeout:
        return create_error_response(504, "Dịch vụ TTS phản hồi quá lâu (Timeout)")
    except Exception as e:
        return create_error_response(500, f"Lỗi máy chủ khi tạo giọng nói: {str(e)}")

# --- CHẠY SERVER ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 Hệ thống đã sẵn sàng phát triển tại: http://localhost:{port}")
    # Đặt debug=False cho môi trường production để có hiệu suất tối ưu và an toàn nhất
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
