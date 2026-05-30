#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  ✨ ULTIMATE AI PYTHON – TITAN EDITION v9.0 (FULL MODELS)      ║
║  Tất cả model từ Ckey.vn, phân loại FREE/PAID, hiển thị giá    ║
║  Giao diện siêu đẹp, Tìm kiếm model, Quản lý phiên, TTS, Ảnh  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import requests, json, time, re, sys, os, threading, itertools, math, subprocess

# ==================== 1. PROVIDERS & MODELS (ĐẦY ĐỦ) ====================
PROVIDERS = {
    "ckey": {
        "name": "Ckey.vn",
        "api_key": "sk-e317a237354192e26f99951f06e4882779e8a0e08e86d2f71242e8ff770bdf24",
        "endpoints": {
            "text": "https://ckey.vn/v1/chat/completions",
            "embed": "https://ckey.vn/v1/embeddings",
            "image": "https://ckey.vn/v1/images/generations",
            "tts": "https://ckey.vn/v1/audio/speech"
        },
        "models": [
            # Text FREE (input & output = 1 VND)
            {"name": "chieustudio/mistral-large-3-675b-instruct-2512", "type": "text", "tier": "FREE", "desc": "Mistral Large 3 675B", "pricing": "1/1"},
            {"name": "mistral-small-4-119b-2603", "type": "text", "tier": "FREE", "desc": "Mistral Small 4", "pricing": "1/1"},
            {"name": "chieustudio/deepseek-r1", "type": "text", "tier": "FREE", "desc": "DeepSeek R1", "pricing": "1/1"},
            {"name": "mistral-medium-3.5-128b", "type": "text", "tier": "FREE", "desc": "Mistral Medium 3.5", "pricing": "1/1"},
            {"name": "qwen3-coder-480b-a35b-instruct", "type": "text", "tier": "FREE", "desc": "Qwen3 Coder 480B", "pricing": "1/1"},
            {"name": "glm4.7", "type": "text", "tier": "FREE", "desc": "GLM 4.7", "pricing": "1/1"},
            # Text PAID (có giá >1 VND)
            {"name": "deepseek-r1-distill-qwen-32b", "type": "text", "tier": "PAID", "desc": "DeepSeek R1 Distill", "pricing": "120/120"},
            {"name": "deepseek-3.2", "type": "text", "tier": "PAID", "desc": "DeepSeek 3.2", "pricing": "112/168"},
            {"name": "qwen3-coder-next", "type": "text", "tier": "PAID", "desc": "Qwen3 Coder Next", "pricing": "60/320"},
            {"name": "minimax-m2.5", "type": "text", "tier": "PAID", "desc": "Minimax M2.5", "pricing": "120/480"},
            {"name": "minimax-m2.1", "type": "text", "tier": "PAID", "desc": "Minimax M2.1", "pricing": "108/480"},
            {"name": "mistral-large-3-675b-instruct-2512", "type": "text", "tier": "PAID", "desc": "Mistral Large 3 675B", "pricing": "200/600"},
            {"name": "deepseek-v4-flash", "type": "text", "tier": "PAID", "desc": "DeepSeek V4 Flash", "pricing": "322/644"},
            {"name": "kimi-k2.5", "type": "text", "tier": "PAID", "desc": "Kimi K2.5", "pricing": "240/1000"},
            {"name": "glm-5", "type": "text", "tier": "PAID", "desc": "GLM-5", "pricing": "400/1280"},
            {"name": "kimi-k2.6", "type": "text", "tier": "PAID", "desc": "Kimi K2.6", "pricing": "296/1400"},
            {"name": "gpt-5.4-mini", "type": "text", "tier": "PAID", "desc": "GPT 5.4 Mini", "pricing": "300/2400"},
            {"name": "claude-haiku-4.5", "type": "text", "tier": "PAID", "desc": "Claude Haiku 4.5", "pricing": "600/3000"},
            {"name": "gpt-5.2", "type": "text", "tier": "PAID", "desc": "GPT 5.2", "pricing": "500/4000"},
            {"name": "deepseek-v4-pro", "type": "text", "tier": "PAID", "desc": "DeepSeek V4 Pro", "pricing": "1000/5000"},
            {"name": "gpt-5.3-codex", "type": "text", "tier": "PAID", "desc": "GPT 5.3 Codex", "pricing": "700/5600"},
            {"name": "gpt-5.4", "type": "text", "tier": "PAID", "desc": "GPT 5.4", "pricing": "1000/8000"},
            {"name": "claude-sonnet-4.6", "type": "text", "tier": "PAID", "desc": "Claude Sonnet 4.6", "pricing": "1800/9000"},
            {"name": "gpt-5.5", "type": "text", "tier": "PAID", "desc": "GPT 5.5", "pricing": "2000/12000"},
            {"name": "claude-opus-4.6", "type": "text", "tier": "PAID", "desc": "Claude Opus 4.6", "pricing": "4000/12000"},
            # Thêm các model khác (rút gọn)
            {"name": "phuocanh421994/Qwen3.6 27b", "type": "text", "tier": "PAID", "desc": "Qwen3.6 27B", "pricing": "500/1000"},
            {"name": "vykelongthuong/Deepseek V4 Flash", "type": "text", "tier": "PAID", "desc": "Deepseek V4 Flash", "pricing": "300/1000"},
            {"name": "phuocanh421994/Qwen3.6 35b a3b", "type": "text", "tier": "PAID", "desc": "Qwen3.6 35B", "pricing": "600/1200"},
            {"name": "phuocanh421994/Qwen3.6-Flash", "type": "text", "tier": "PAID", "desc": "Qwen3.6 Flash", "pricing": "650/1300"},
            {"name": "phuocanh421994/Deepseek V4 Pro", "type": "text", "tier": "PAID", "desc": "Deepseek V4 Pro", "pricing": "700/1400"},
            {"name": "phuocanh421994/Qwen 3.6 Max Preview", "type": "text", "tier": "PAID", "desc": "Qwen 3.6 Max", "pricing": "800/2400"},
            {"name": "glm-5.1", "type": "text", "tier": "PAID", "desc": "GLM-5.1", "pricing": "500/2500"},
            {"name": "phuocanh421994/Qwen 3.6 Plus", "type": "text", "tier": "PAID", "desc": "Qwen 3.6 Plus", "pricing": "1000/2500"},
            {"name": "hiennqhust/qwen3.6-27b", "type": "text", "tier": "PAID", "desc": "Qwen3.6 27B", "pricing": "500/3000"},
            {"name": "phuocanh421994/Qwen3.5 Plus", "type": "text", "tier": "PAID", "desc": "Qwen3.5 Plus", "pricing": "1000/3000"},
            {"name": "hiennqhust/gpt-5.4", "type": "text", "tier": "PAID", "desc": "GPT 5.4", "pricing": "800/3000"},
            {"name": "phuocanh421994/Qwen3 Coder Plus", "type": "text", "tier": "PAID", "desc": "Qwen3 Coder Plus", "pricing": "1200/5000"},
            {"name": "phuocanh421994/Qwen3 Max", "type": "text", "tier": "PAID", "desc": "Qwen3 Max", "pricing": "1500/5000"},
            {"name": "phuocanh421994/Qwen 3.7 max", "type": "text", "tier": "PAID", "desc": "Qwen 3.7 Max", "pricing": "1500/7500"},
            {"name": "claude-sonnet-4.5", "type": "text", "tier": "PAID", "desc": "Claude Sonnet 4.5", "pricing": "1800/9000"},
            {"name": "claude-sonnet-4-5", "type": "text", "tier": "PAID", "desc": "Claude Sonnet 4 5", "pricing": "1800/9000"},
            # Embed FREE
            {"name": "text-embedding-3-small", "type": "embed", "tier": "FREE", "desc": "Text Embedding 3 Small", "pricing": "1/1"},
            {"name": "gemini-embedding-001", "type": "embed", "tier": "FREE", "desc": "Gemini Embedding 001", "pricing": "1/1"},
            {"name": "llama-nemotron-embed-vl-1b-v2", "type": "embed", "tier": "FREE", "desc": "Llama Nemotron Embed", "pricing": "1/1"},
            {"name": "pplx-embed-v1-4b", "type": "embed", "tier": "FREE", "desc": "PPLX Embed v1 4B", "pricing": "1/1"},
            {"name": "gemini-embedding-2-preview", "type": "embed", "tier": "FREE", "desc": "Gemini Embedding 2", "pricing": "1/1"},
            # Image PAID
            {"name": "imagen-3.5", "type": "image", "tier": "PAID", "desc": "Imagen 3.5", "pricing": "Req:?"},
            {"name": "gem-pix-2", "type": "image", "tier": "PAID", "desc": "Gem Pix 2", "pricing": "Req:?"},
            {"name": "thanhnhan9023/gpt-image-2", "type": "image", "tier": "PAID", "desc": "GPT Image 2", "pricing": "1600/req"},
            # TTS FREE (per request = 1 VND)
            {"name": "vi-VN-NamMinhNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nam", "voice": "NamMinh", "pricing": "1/req"},
            {"name": "vi-VN-HoaiMyNeural", "type": "tts", "tier": "FREE", "desc": "Giọng nữ", "voice": "HoaiMy", "pricing": "1/req"},
            {"name": "google-tts/vi", "type": "tts", "tier": "FREE", "desc": "Google TTS", "voice": "alloy", "pricing": "1/req"},
        ]
    },
    "cocolink": {
        "name": "Cocolink.ai",
        "api_key": "sk-fAC9npWdz1ynogX_Ppt0Xdi44Sm_aIIXLrJRE1AAoIyelVGvMl4KXGdgn3U",
        "endpoints": {
            "text": "https://www.cocolink.ai/v1/chat/completions",
            "embed": "https://www.cocolink.ai/v1/embeddings",
            "image": None,
            "tts": None
        },
        "models": [
            {"name": "qwen-plus", "type": "text", "tier": "PAID", "desc": "Qwen Plus", "pricing": "?"},
            {"name": "qwen-turbo", "type": "text", "tier": "PAID", "desc": "Qwen Turbo", "pricing": "?"},
            {"name": "qwen3-coder-flash", "type": "text", "tier": "PAID", "desc": "Qwen3 Coder Flash", "pricing": "?"},
            {"name": "qwen3.5-flash", "type": "text", "tier": "PAID", "desc": "Qwen 3.5 Flash", "pricing": "?"},
            {"name": "text-embedding-v4", "type": "embed", "tier": "FREE", "desc": "Text Embedding V4", "pricing": "?"},
        ]
    }
}

# ==================== 2. COLOR & DISPLAY ====================
USE_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
class C:
    R='\033[91m' if USE_COLOR else ''; G='\033[92m' if USE_COLOR else ''
    Y='\033[93m' if USE_COLOR else ''; B='\033[94m' if USE_COLOR else ''
    M='\033[95m' if USE_COLOR else ''; CY='\033[96m' if USE_COLOR else ''
    W='\033[97m' if USE_COLOR else ''; DIM='\033[2m' if USE_COLOR else ''
    BOLD='\033[1m' if USE_COLOR else ''; RST='\033[0m' if USE_COLOR else ''

def cprint(t, c="", end="\n"): print(f"{c}{t}{C.RST}", end=end)
def safe_input(p, c=C.W):
    try: return input(f"{c}{p}{C.RST}")
    except (KeyboardInterrupt, EOFError): cprint("\n👋 Tạm biệt!", C.G); sys.exit(0)

def box(title, content, width=70, color=C.CY):
    cprint("╔" + "═"*(width-2) + "╗", color)
    cprint("║ " + title.center(width-4) + " ║", color)
    cprint("╠" + "═"*(width-2) + "╣", color)
    for line in content:
        cprint("║ " + line.ljust(width-4) + " ║", C.W)
    cprint("╚" + "═"*(width-2) + "╝", color)

def spinner(msg="Đang xử lý"):
    return _Spinner(msg)

class _Spinner:
    def __init__(self, msg): self.msg=msg; self.run=False; self.t=None
    def _spin(self):
        for ch in itertools.cycle('⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'):
            if not self.run: break
            sys.stdout.write(f'\r{C.Y}{ch} {self.msg}...{C.RST}'); sys.stdout.flush(); time.sleep(0.1)
    def start(self): self.run=True; self.t=threading.Thread(target=self._spin,daemon=True); self.t.start()
    def stop(self):
        self.run=False
        if self.t: self.t.join(timeout=0.5)
        sys.stdout.write('\r'+' '*(len(self.msg)+20)+'\r'); sys.stdout.flush()

# ==================== 3. UTILS ====================
def clean_text(t):
    m = re.search(r"<think>(.*?)</think>", t, re.DOTALL)
    if m: t = t[m.end():].strip()
    return re.sub(r'<\w+:tool_call>.*?</\w+:tool_call>', '', t, flags=re.DOTALL).strip()

def cosine_sim(v1, v2):
    dot = sum(a*b for a,b in zip(v1,v2))
    n1 = math.sqrt(sum(a*a for a in v1))
    n2 = math.sqrt(sum(b*b for b in v2))
    return dot/(n1*n2) if n1*n2 else 0

# ==================== 4. CONFIG & SESSION ====================
class Config:
    FILE = "ultimate_config.json"
    def __init__(self):
        self.data = {"provider":"ckey","model":"","temp":0.7,"max_tok":4096,"mode":"stream","show_think":False,"system_prompt":"","voice":"NamMinh","favorites":[],"current_session":"default"}
        self.load()
    def load(self):
        try:
            if os.path.exists(self.FILE):
                with open(self.FILE, encoding='utf-8') as f:
                    self.data.update(json.load(f))
        except: pass
    def save(self):
        try:
            with open(self.FILE,"w", encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except: pass

class Session:
    def __init__(self):
        self.messages = []
        self.embed_store = {}
        self.total_prompt_tok = 0
        self.total_comp_tok = 0
        self.last_resp = ""
        self.last_usage = {}
    def add(self, role, content):
        self.messages.append({"role":role,"content":content})
    def clear(self):
        self.messages.clear()
        self.total_prompt_tok = self.total_comp_tok = 0
        self.last_resp = ""
    def export_chat(self, filename="chat_export.txt"):
        with open(filename,"w", encoding="utf-8") as f:
            for m in self.messages:
                role = "Bạn" if m["role"]=="user" else "AI"
                f.write(f"{role}: {m['content']}\n\n")
        return filename

class SessionManager:
    def __init__(self):
        self.sessions = {"default": Session()}
        self.current = "default"
    def new(self, name):
        if name in self.sessions:
            self.current = name
            return self.sessions[name]
        self.sessions[name] = Session()
        self.current = name
        return self.sessions[name]
    def switch(self, name):
        if name in self.sessions:
            self.current = name
            return self.sessions[name]
        return None
    def active(self):
        return self.sessions[self.current]
    def list_sessions(self):
        return list(self.sessions.keys())
    def delete(self, name):
        if name == "default": return False
        if name in self.sessions:
            del self.sessions[name]
            if self.current == name:
                self.current = "default"
            return True
        return False

# ==================== 5. API CLIENT ====================
class APIClient:
    def __init__(self, provider_key, config):
        self.provider_key = provider_key
        self.config = config
        self.provider = PROVIDERS[provider_key]
        self.session = requests.Session()
        self.session.headers.update({"Content-Type":"application/json"})
        self.timeout = 120
        self.retries = 3
    @property
    def api_key(self): return self.provider["api_key"]
    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type":"application/json"}
    def call(self, endpoint_key, payload, stream=False):
        url = self.provider["endpoints"].get(endpoint_key)
        if not url: return None
        headers = self._headers()
        for attempt in range(self.retries):
            try:
                if stream:
                    return requests.post(url, headers=headers, json=payload, stream=True, timeout=self.timeout)
                else:
                    resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                    if resp.status_code == 200: return resp.json()
                    if resp.status_code in (429,500,502,503,504):
                        time.sleep(2**attempt)
                    else:
                        cprint(f"❌ HTTP {resp.status_code}: {resp.text[:200]}", C.R)
                        return None
            except Exception as e:
                cprint(f"🔥 Lỗi mạng: {e}", C.R)
                if attempt < self.retries-1: time.sleep(2**attempt)
                else: return None
        return None
    def ping(self, model_name):
        payload = {"model":model_name,"messages":[{"role":"user","content":"ping"}],"max_tokens":5}
        t0 = time.time()
        resp = self.call("text", payload)
        if resp: return time.time()-t0
        return None

# ==================== 6. CHAT ENGINE ====================
class ChatEngine:
    def __init__(self, api_client, config, session_getter):
        self.api = api_client; self.cfg = config; self.get_session = session_getter
    @property
    def sess(self): return self.get_session()
    def _build_payload(self, stream, extra_max_tok=None):
        msgs = []
        if self.cfg.data["system_prompt"]:
            msgs.append({"role":"system","content":self.cfg.data["system_prompt"]})
        msgs.extend(self.sess.messages)
        p = {"model":self.cfg.data["model"],"messages":msgs,"temperature":self.cfg.data["temp"],"stream":stream}
        if extra_max_tok: p["max_tokens"] = extra_max_tok
        else: p["max_tokens"] = self.cfg.data["max_tok"]
        return p
    def chat(self, stream=True):
        if not stream: return self._nonstream_chat()
        return self._stream_chat()
    def _nonstream_chat(self):
        full = ""; usage = {}
        cur_msgs = self.sess.messages.copy()
        spin = spinner("Đang suy nghĩ"); spin.start()
        try:
            while True:
                payload = self._build_payload(False, extra_max_tok=4096)
                data = self.api.call("text", payload)
                if not data: break
                choices = data.get("choices",[])
                if not choices: break
                msg = choices[0]["message"]["content"]; finish = choices[0].get("finish_reason","stop")
                full += msg
                if "usage" in data:
                    for k in ["prompt_tokens","completion_tokens","total_tokens"]:
                        usage[k] = usage.get(k,0) + data["usage"].get(k,0)
                if finish != "length": break
                cur_msgs.append({"role":"assistant","content":msg})
                spin.stop(); spin = spinner("Tiếp tục"); spin.start()
        finally: spin.stop()
        return full, usage
    def _stream_chat(self):
        full = ""; usage = {}
        cprint("\n🤖 Trợ lý: ", C.G+C.BOLD, end="")
        payload = self._build_payload(True, extra_max_tok=32768)
        resp = self.api.call("text", payload, stream=True)
        if not resp: return None, None
        in_think = False
        spin2 = spinner("Đang nhận token"); spin2.start()
        try:
            for line in resp.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    d = line[5:].strip()
                    if d == "[DONE]": break
                    try:
                        chunk = json.loads(d)
                        if "choices" in chunk:
                            tok = chunk["choices"][0].get("delta",{}).get("content","")
                            if tok:
                                full += tok
                                if not self.cfg.data["show_think"]:
                                    i=0
                                    while i < len(tok):
                                        if not in_think:
                                            pos = tok.find("<think>", i)
                                            if pos==-1:
                                                sys.stdout.write(tok[i:]); sys.stdout.flush(); break
                                            else:
                                                sys.stdout.write(tok[i:pos]); sys.stdout.flush()
                                                in_think=True; i=pos+len("<think>")
                                        else:
                                            pos = tok.find("</think>", i)
                                            if pos==-1: break
                                            else: in_think=False; i=pos+len("</think>")
                                else:
                                    sys.stdout.write(tok); sys.stdout.flush()
                        if "usage" in chunk: usage = chunk["usage"]
                    except: pass
            print()
        except Exception as e: cprint(f"\n🔥 Lỗi stream: {e}", C.R)
        finally: spin2.stop()
        return full, usage

# ==================== 7. EMBEDDING SERVICE ====================
class EmbeddingService:
    def __init__(self, api_client, config, session_getter):
        self.api = api_client; self.cfg = config; self.get_session = session_getter
    @property
    def sess(self): return self.get_session()
    def embed(self, text, label=None):
        payload = {"model":self.cfg.data["model"],"input":text}
        data = self.api.call("embed", payload)
        if not data: return None
        vec = data["data"][0]["embedding"]
        cprint(f"✅ Embedding ({len(vec)}D): [{', '.join(f'{x:.4f}' for x in vec[:6])} ...]", C.G)
        if label: self.sess.embed_store[label] = vec; cprint(f"📌 Nhãn: {label}", C.Y)
        else: self.sess.embed_store["last"] = vec
        return vec
    def compare(self, lab1, lab2):
        if lab1 not in self.sess.embed_store or lab2 not in self.sess.embed_store:
            cprint("❌ Nhãn không tồn tại.", C.R); return None
        sim = cosine_sim(self.sess.embed_store[lab1], self.sess.embed_store[lab2])
        bar = "█"*int(sim*20) + "░"*(20-int(sim*20))
        cprint(f"🔍 {lab1} ↔ {lab2}: [{bar}] {sim*100:.1f}%", C.M)
        return sim

# ==================== 8. IMAGE & TTS SERVICE ====================
class MediaService:
    def __init__(self, api_client, config):
        self.api = api_client; self.cfg = config
    def generate_image(self, prompt):
        payload = {"model":self.cfg.data["model"],"prompt":prompt,"n":1,"size":"1024x1024"}
        data = self.api.call("image", payload)
        if not data: return None
        url = data["data"][0]["url"]
        cprint(f"🖼️  {url}", C.G)
        try:
            import webbrowser; webbrowser.open(url)
        except: pass
        return url
    def text_to_speech(self, text, voice=None):
        if not voice: voice = self.cfg.data.get("voice","NamMinh")
        payload = {"model":self.cfg.data["model"],"input":text,"voice":voice}
        url = self.api.provider["endpoints"].get("tts")
        if not url:
            cprint("❌ Provider không hỗ trợ TTS.", C.R); return
        try:
            resp = requests.post(url, headers=self.api._headers(), json=payload, timeout=120)
            if resp.status_code == 200:
                fname = f"tts_{int(time.time())}.mp3"
                with open(fname,"wb") as f: f.write(resp.content)
                cprint(f"🔊 {fname}", C.G)
                try:
                    import sound; sound.Player(fname).play()
                except: pass
                return fname
            else: cprint(f"❌ TTS lỗi {resp.status_code}", C.R)
        except Exception as e: cprint(f"🔥 Lỗi TTS: {e}", C.R)

# ==================== 9. ULTIMATE BOT V9.0 ====================
class UltimateBot:
    def __init__(self):
        self.cfg = Config()
        self._ensure_model()
        self.api = APIClient(self.cfg.data["provider"], self.cfg)
        self.sess_mgr = SessionManager()
        saved_session = self.cfg.data.get("current_session", "default")
        if saved_session != "default" and saved_session in self.sess_mgr.sessions:
            self.sess_mgr.current = saved_session
        self.chat_engine = ChatEngine(self.api, self.cfg, lambda: self.sess)
        self.embed_service = EmbeddingService(self.api, self.cfg, lambda: self.sess)
        self.media_service = MediaService(self.api, self.cfg)
        self.command_history = []
        self.auto_suggest = False
        cprint("✨ Ultimate AI Python v9.0 – Tất cả model + Giá hiển thị đẹp", C.CY)

    @property
    def sess(self): return self.sess_mgr.active()

    def _ensure_model(self):
        provider = PROVIDERS[self.cfg.data["provider"]]
        if not any(m["name"]==self.cfg.data["model"] for m in provider["models"]):
            for m in provider["models"]:
                if m["type"] == "text":
                    self.cfg.data["model"] = m["name"]; self.cfg.save(); return
            self.cfg.data["model"] = provider["models"][0]["name"]; self.cfg.save()

    def _get_current_model(self):
        provider = PROVIDERS[self.cfg.data["provider"]]
        for m in provider["models"]:
            if m["name"] == self.cfg.data["model"]: return m
        return provider["models"][0]

    def _switch_model_type(self, req_type):
        m = self._get_current_model()
        if m["type"] != req_type:
            provider = PROVIDERS[self.cfg.data["provider"]]
            for mod in provider["models"]:
                if mod["type"] == req_type:
                    self.cfg.data["model"] = mod["name"]; self.cfg.save()
                    cprint(f"⚠️ Đã chuyển sang {mod['name']}", C.Y)
                    return True
            cprint(f"❌ Provider không hỗ trợ {req_type}.", C.R); return False
        return True

    def _do_chat(self):
        if not self._switch_model_type("text"): return
        t0 = time.time()
        if self.cfg.data["mode"] == "stream":
            text, usage = self.chat_engine.chat(stream=True)
        else:
            text, usage = self.chat_engine.chat(stream=False)
            if text:
                clean = clean_text(text) if not self.cfg.data["show_think"] else text
                cprint("💬 Phản hồi:", C.G+C.BOLD); cprint(clean, C.W)
        elapsed = time.time()-t0
        if text:
            self.sess.add("assistant", text)
            self.sess.last_resp = text; self.sess.last_usage = usage or {}
            if usage:
                pt = usage.get('prompt_tokens',0); ct = usage.get('completion_tokens',0)
                tt = usage.get('total_tokens',0)
                self.sess.total_prompt_tok += pt; self.sess.total_comp_tok += ct
                cprint(f"📊 Prompt: {pt} | Completion: {ct} | Total: {tt} | {ct/elapsed:.1f} tok/s", C.CY)
        else: cprint("❌ Không có phản hồi.", C.R)

    # ==================== HIỂN THỊ MODEL ĐẸP ====================
    def _show_all_models(self, provider_key=None):
        if provider_key:
            providers = {provider_key: PROVIDERS[provider_key]}
        else:
            providers = PROVIDERS
        for pkey, pdata in providers.items():
            cprint(f"\n🔌 {pdata['name']} ({pkey}): {len(pdata['models'])} models", C.Y+C.BOLD)
            # Gom nhóm theo type
            type_groups = {}
            for m in pdata["models"]:
                type_groups.setdefault(m["type"], []).append(m)
            type_order = {"text":"💬 Text","embed":"🧠 Embed","image":"🖼️ Image","tts":"🔊 TTS"}
            for mtype, mlabel in type_order.items():
                if mtype not in type_groups: continue
                cprint(f"  {mlabel}:", C.CY)
                # Sắp xếp: FREE trước, PAID sau
                free = [m for m in type_groups[mtype] if m["tier"]=="FREE"]
                paid = [m for m in type_groups[mtype] if m["tier"]=="PAID"]
                if free:
                    cprint("    🆓 FREE:", C.G)
                    for m in free:
                        price_str = m.get("pricing","?")
                        cprint(f"      {m['name']:<45} {C.DIM}{m['desc']:<20} Giá: {price_str}{C.RST}", C.W)
                if paid:
                    cprint("    💰 PAID:", C.R)
                    for m in paid:
                        price_str = m.get("pricing","?")
                        cprint(f"      {m['name']:<45} {C.DIM}{m['desc']:<20} Giá: {price_str}{C.RST}", C.W)
        safe_input("\nNhấn Enter để quay lại...", C.DIM)

    # ==================== MENU CHÍNH ====================
    def _main_menu(self):
        while True:
            cprint("\n" + "═"*50, C.CY)
            cprint("  📋 MENU CHÍNH", C.CY+C.BOLD)
            cprint("═"*50, C.CY)
            cprint("  1. 💬 Chat với AI")
            cprint("  2. 🧠 Embedding")
            cprint("  3. 🔍 So sánh Embedding")
            cprint("  4. 🖼️  Tạo ảnh")
            cprint("  5. 🔊 TTS")
            cprint("  6. ⚙️  Cài đặt (Provider/Model)")
            cprint("  7. 📋 Xem tất cả model (có giá)")
            cprint("  8. 💾 Quản lý phiên")
            cprint("  9. 🚪 Thoát")
            cprint("═"*50, C.CY)
            ch = safe_input("👉 Chọn (1-9): ", C.CY).strip()
            if ch == "1": self._chat_mode()
            elif ch == "2": self._embed_mode()
            elif ch == "3": self._compare_mode()
            elif ch == "4": self._image_mode()
            elif ch == "5": self._tts_mode()
            elif ch == "6": self._settings_menu()
            elif ch == "7": self._show_all_models()
            elif ch == "8": self._session_menu()
            elif ch == "9":
                self.cfg.data["current_session"] = self.sess_mgr.current
                self.cfg.save()
                cprint("👋 Tạm biệt!", C.G); break
            else: cprint("❌ Lựa chọn không hợp lệ.", C.R)

    # ==================== CHAT MODE (GIỮ NGUYÊN CÁC LỆNH) ====================
    def _chat_mode(self):
        cprint(f"\n💬 Chat: {self.cfg.data['model']} ({PROVIDERS[self.cfg.data['provider']]['name']})", C.G)
        cprint("Lệnh: /help, /provider, /model, /models, /mode, /temp, /maxtokens, /system, /showthink, /raw, /clear, /history, /export, /retry, /copy, /ping, /status, /session, /menu, /exit", C.Y)
        while True:
            ui = safe_input("\n👤 Bạn: ", C.B)
            if ui.lower() == "/exit": break
            if ui.lower() == "/menu": break
            if ui.startswith("/"):
                self._handle_chat_command(ui)
                continue
            if not ui.strip(): continue
            self.sess.add("user", ui)
            self._do_chat()

    def _handle_chat_command(self, ui):
        parts = ui.split(); base = parts[0].lower()
        if base == "/help": self._show_help()
        elif base == "/provider": self._change_provider()
        elif base == "/model": self._change_model()
        elif base == "/models": self._show_all_models(self.cfg.data["provider"])
        elif base == "/mode":
            if len(parts)>1 and parts[1] in ("stream","nonstream"):
                self.cfg.data["mode"] = "nonstream" if parts[1]=="nonstream" else "stream"
                self.cfg.save(); cprint(f"✅ {self.cfg.data['mode']}", C.G)
            else: cprint("❌ /mode stream|nonstream", C.R)
        elif base == "/temp":
            try: self.cfg.data["temp"] = float(parts[1]); self.cfg.save(); cprint(f"✅ Temp={self.cfg.data['temp']}", C.G)
            except: cprint("❌ Sai.", C.R)
        elif base == "/maxtokens":
            try: self.cfg.data["max_tok"] = int(parts[1]); self.cfg.save(); cprint(f"✅ Max tokens={self.cfg.data['max_tok']}", C.G)
            except: cprint("❌ Sai.", C.R)
        elif base == "/system":
            prompt = ui[len("/system "):].strip()
            self.cfg.data["system_prompt"] = prompt if prompt else ""
            self.cfg.save(); cprint(f"✅ System prompt {'đã đặt' if prompt else 'đã xóa'}.", C.G)
        elif base == "/showthink":
            self.cfg.data["show_think"] = not self.cfg.data["show_think"]; self.cfg.save()
            cprint(f"Show think: {'Bật' if self.cfg.data['show_think'] else 'Tắt'}", C.G)
        elif base == "/raw":
            self.cfg.data["raw"] = not self.cfg.data.get("raw", False); self.cfg.save()
            cprint(f"Raw JSON: {'Bật' if self.cfg.data.get('raw', False) else 'Tắt'}", C.G)
        elif base == "/clear":
            self.sess.clear(); cprint("✅ Đã xóa lịch sử chat.", C.G)
        elif base == "/history": self._show_history()
        elif base == "/export":
            fname = self.sess.export_chat(); cprint(f"✅ Đã lưu {fname}", C.G)
        elif base == "/retry": self._retry_last()
        elif base == "/copy": self._copy_last_response()
        elif base == "/ping": self._ping()
        elif base == "/status": self._show_status()
        elif base == "/session": self._session_menu()
        elif base == "/favorite": self._add_to_favorites()
        elif base == "/favorites": self._list_favorites()
        elif base == "/search": self._search_model(parts)
        else: cprint("❓ Lệnh không rõ. /help", C.R)

    def _show_help(self):
        help_lines = [
            "/help - Trợ giúp",
            "/provider - Đổi nhà cung cấp",
            "/model - Đổi model",
            "/models - Xem tất cả model + giá",
            "/mode stream|nonstream - Chế độ",
            "/temp 0.8 - Temperature",
            "/maxtokens 2048 - Max tokens",
            "/system <text> - System prompt",
            "/showthink - Bật/tắt suy nghĩ",
            "/raw - Bật/tắt JSON thô",
            "/clear - Xóa lịch sử chat",
            "/history - Xem lịch sử",
            "/export - Lưu lịch sử",
            "/retry - Thử lại câu cuối",
            "/copy - Copy câu trả lời",
            "/ping - Kiểm tra độ trễ",
            "/status - Trạng thái",
            "/session - Quản lý phiên",
            "/favorite - Thêm model yêu thích",
            "/favorites - Xem model yêu thích",
            "/search <từ khóa> - Tìm model",
            "/menu - Quay lại menu chính",
            "/exit - Thoát"
        ]
        box("TRỢ GIÚP", help_lines, 60, C.CY)

    # Các hàm phụ trợ (change_provider, change_model, ...) giữ nguyên nhưng cập nhật hiển thị model đẹp hơn
    def _change_provider(self):
        cprint("\n📡 Nhà cung cấp:", C.CY)
        for i, (k, v) in enumerate(PROVIDERS.items(), 1):
            cprint(f"  {i}. {v['name']} ({len(v['models'])} models)", C.W)
        ch = safe_input("👉 Chọn số: ", C.CY).strip()
        if ch.isdigit() and 1 <= int(ch) <= len(PROVIDERS):
            self.cfg.data["provider"] = list(PROVIDERS.keys())[int(ch)-1]
            self.api = APIClient(self.cfg.data["provider"], self.cfg)
            self._ensure_model()
            self.cfg.save()
            cprint(f"✅ Đã chọn: {PROVIDERS[self.cfg.data['provider']]['name']}", C.G)
        else: cprint("❌ Giữ nguyên.", C.R)

    def _change_model(self):
        provider = PROVIDERS[self.cfg.data["provider"]]
        models = provider["models"]
        self._show_all_models(self.cfg.data["provider"])
        ch = safe_input("👉 Nhập tên model (hoặc một phần): ", C.CY).strip()
        if not ch: return
        matches = [m for m in models if ch.lower() in m["name"].lower()]
        if len(matches) == 1:
            self.cfg.data["model"] = matches[0]["name"]
            cprint(f"✅ Đã chọn: {matches[0]['name']} ({matches[0]['type']}/{matches[0]['tier']})", C.G)
            self.cfg.save()
        elif len(matches) > 1:
            cprint("🔍 Nhiều model khớp, hãy chọn số:", C.Y)
            for i, m in enumerate(matches, 1):
                cprint(f"  {i}. {m['name']} ({m['type']}/{m['tier']}) - Giá: {m.get('pricing','?')}", C.W)
            sel = safe_input("Chọn số: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(matches):
                self.cfg.data["model"] = matches[int(sel)-1]["name"]
                self.cfg.save()
                cprint(f"✅ Đã chọn: {self.cfg.data['model']}", C.G)
        else:
            cprint("❌ Không tìm thấy model.", C.R)

    def _show_history(self):
        if not self.sess.messages: cprint("ℹ️ Chưa có tin nhắn.", C.Y); return
        page_size = 5; total = len(self.sess.messages)
        total_pages = (total+page_size-1)//page_size; page = 0
        while True:
            start = page*page_size; end = min(start+page_size, total)
            cprint(f"\n📜 Lịch sử (Trang {page+1}/{total_pages}):", C.CY)
            for i in range(start, end):
                m = self.sess.messages[i]; role = "👤" if m["role"]=="user" else "🤖"
                txt = m["content"][:100] + ("..." if len(m["content"])>100 else "")
                cprint(f"  {i+1}. {role}: {txt}", C.DIM)
            if total_pages <= 1: break
            cprint("  [N]ext, [P]rev, [Q]uit", C.Y)
            cmd = safe_input("  > ").strip().lower()
            if cmd == 'n' and page < total_pages-1: page += 1
            elif cmd == 'p' and page > 0: page -= 1
            elif cmd == 'q': break
            else: cprint("❌ Không hợp lệ.", C.R)

    def _retry_last(self):
        if self.sess.messages and self.sess.messages[-1]["role"]=="user":
            last = self.sess.messages[-1]["content"]
            if len(self.sess.messages)>=2 and self.sess.messages[-2]["role"]=="user":
                self.sess.messages.pop()
            self.sess.add("user", last)
            self._do_chat()
        else: cprint("❌ Không có câu hỏi cuối.", C.R)

    def _copy_last_response(self):
        if self.sess.last_resp:
            clean = clean_text(self.sess.last_resp) if not self.cfg.data["show_think"] else self.sess.last_resp
            try:
                if sys.platform=="darwin": subprocess.run("pbcopy", text=True, input=clean)
                elif sys.platform=="win32": subprocess.run("clip", text=True, input=clean)
                else: subprocess.run("xclip -selection clipboard", shell=True, text=True, input=clean)
                cprint("📋 Đã copy!", C.G)
            except Exception as e: cprint(f"❌ Lỗi copy: {e}", C.R)
        else: cprint("❌ Chưa có phản hồi.", C.R)

    def _ping(self):
        model = self.cfg.data["model"]
        cprint(f"🔍 Ping {model}...", C.Y)
        elapsed = self.api.ping(model)
        if elapsed: cprint(f"✅ {elapsed*1000:.0f} ms", C.G)
        else: cprint("❌ Ping thất bại.", C.R)

    def _show_status(self):
        m = self._get_current_model()
        lines = [
            f"Provider: {PROVIDERS[self.cfg.data['provider']]['name']}",
            f"Model: {m['name']} ({m['type']}/{m['tier']})",
            f"Giá: {m.get('pricing','?')}",
            f"Mode: {self.cfg.data['mode']} | Temp: {self.cfg.data['temp']} | Max Tok: {self.cfg.data['max_tok']}",
            f"System prompt: {'Có' if self.cfg.data['system_prompt'] else 'Không'}",
            f"Show think: {'Bật' if self.cfg.data['show_think'] else 'Tắt'}",
            f"Tổng token: P:{self.sess.total_prompt_tok} C:{self.sess.total_comp_tok}",
            f"Tin nhắn: {len(self.sess.messages)} | Embed labels: {len(self.sess.embed_store)}",
            f"Phiên: {self.sess_mgr.current}"
        ]
        box("TRẠNG THÁI", lines, 60, C.CY)

    def _embed_mode(self):
        if not self._switch_model_type("embed"): return
        cprint(f"\n🧠 Embedding với {self.cfg.data['model']}", C.G)
        cprint("Nhập văn bản để nhúng. /label <nhãn> <text>, /compare <lab1> <lab2>, /batch <text1>||<text2>, /menu", C.Y)
        while True:
            ui = safe_input("\n📌 Embed> ", C.B)
            if ui.lower() == "/menu": break
            if ui.startswith("/label"):
                parts = ui.split()
                if len(parts) >= 3:
                    label = parts[1]; text = " ".join(parts[2:])
                    self.embed_service.embed(text, label)
                else: cprint("❌ /label <nhãn> <văn bản>", C.R)
            elif ui.startswith("/compare"):
                parts = ui.split()
                if len(parts) == 3: self.embed_service.compare(parts[1], parts[2])
                else: cprint("❌ /compare <lab1> <lab2>", C.R)
            elif ui.startswith("/batch"):
                texts = ui[len("/batch "):].strip().split("||")
                for i, t in enumerate(texts, 1):
                    cprint(f"📌 Batch {i}: {t[:50]}...", C.Y)
                    self.embed_service.embed(t.strip(), label=f"batch_{i}")
            elif not ui.strip(): continue
            else: self.embed_service.embed(ui)

    def _compare_mode(self):
        if not self.sess.embed_store: cprint("❌ Chưa có embedding nào.", C.R); return
        cprint("📌 Các nhãn: " + ", ".join(self.sess.embed_store.keys()), C.Y)
        l1 = safe_input("Nhãn 1: ").strip(); l2 = safe_input("Nhãn 2: ").strip()
        self.embed_service.compare(l1, l2)

    def _image_mode(self):
        if not self._switch_model_type("image"): return
        prompt = safe_input("🖼️ Mô tả ảnh: ", C.B)
        if prompt.strip(): self.media_service.generate_image(prompt)

    def _tts_mode(self):
        if not self._switch_model_type("tts"): return
        text = safe_input("🔊 Văn bản: ", C.B)
        if text.strip(): self.media_service.text_to_speech(text)

    def _settings_menu(self):
        while True:
            cprint("\n⚙️ CÀI ĐẶT", C.CY+C.BOLD)
            cprint("  1. Đổi Provider")
            cprint("  2. Đổi Model")
            cprint(f"  3. Temperature: {self.cfg.data['temp']}")
            cprint(f"  4. Max Tokens: {self.cfg.data['max_tok']}")
            cprint(f"  5. Mode: {self.cfg.data['mode']}")
            cprint(f"  6. System Prompt: {'Có' if self.cfg.data['system_prompt'] else 'Không'}")
            cprint(f"  7. Show Think: {'Bật' if self.cfg.data['show_think'] else 'Tắt'}")
            cprint(f"  8. Raw JSON: {'Bật' if self.cfg.data.get('raw', False) else 'Tắt'}")
            cprint(f"  9. Giọng TTS: {self.cfg.data.get('voice','NamMinh')}")
            cprint("  10. Quay lại")
            ch = safe_input("👉 Chọn: ", C.CY).strip()
            if ch == "1": self._change_provider()
            elif ch == "2": self._change_model()
            elif ch == "3":
                try: self.cfg.data["temp"] = float(safe_input("Temperature (0-2): ").strip()); self.cfg.save(); cprint(f"✅ {self.cfg.data['temp']}", C.G)
                except: cprint("❌ Sai.", C.R)
            elif ch == "4":
                try: self.cfg.data["max_tok"] = int(safe_input("Max tokens: ").strip()); self.cfg.save(); cprint(f"✅ {self.cfg.data['max_tok']}", C.G)
                except: cprint("❌ Sai.", C.R)
            elif ch == "5":
                m = safe_input("Mode (stream/nonstream): ").strip().lower()
                if m in ("stream","nonstream"): self.cfg.data["mode"] = "nonstream" if m=="nonstream" else "stream"; self.cfg.save(); cprint(f"✅ {self.cfg.data['mode']}", C.G)
                else: cprint("❌ Sai.", C.R)
            elif ch == "6":
                sp = safe_input("System prompt (trống để xóa): ").strip()
                self.cfg.data["system_prompt"] = sp if sp else ""; self.cfg.save(); cprint("✅ Đã cập nhật.", C.G)
            elif ch == "7":
                self.cfg.data["show_think"] = not self.cfg.data["show_think"]; self.cfg.save(); cprint(f"✅ Show think: {'Bật' if self.cfg.data['show_think'] else 'Tắt'}", C.G)
            elif ch == "8":
                self.cfg.data["raw"] = not self.cfg.data.get("raw", False); self.cfg.save(); cprint(f"✅ Raw JSON: {'Bật' if self.cfg.data.get('raw', False) else 'Tắt'}", C.G)
            elif ch == "9":
                v = safe_input("Giọng TTS (NamMinh/HoaiMy/alloy): ").strip()
                if v: self.cfg.data["voice"] = v; self.cfg.save(); cprint(f"✅ Giọng: {v}", C.G)
            elif ch == "10": break
            else: cprint("❌ Chọn sai.", C.R)

    def _session_menu(self):
        while True:
            cprint("\n💾 QUẢN LÝ PHIÊN", C.CY+C.BOLD)
            cprint(f"  1. Phiên hiện tại: {self.sess_mgr.current}")
            cprint("  2. Tạo phiên mới")
            cprint("  3. Chuyển đổi phiên")
            cprint("  4. Xóa phiên (không thể xóa 'default')")
            cprint("  5. Xuất lịch sử phiên hiện tại")
            cprint("  6. Quay lại")
            ch = safe_input("👉 Chọn: ", C.CY).strip()
            if ch == "1": pass
            elif ch == "2":
                name = safe_input("Tên phiên mới: ").strip()
                if name: self.sess_mgr.new(name); cprint(f"✅ Đã tạo và chuyển sang phiên '{name}'.", C.G)
            elif ch == "3":
                names = self.sess_mgr.list_sessions()
                for i, n in enumerate(names, 1): cprint(f"  {i}. {n}", C.W)
                sel = safe_input("Chọn số: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(names):
                    self.sess_mgr.switch(names[int(sel)-1])
                    cprint(f"✅ Đã chuyển sang phiên '{self.sess_mgr.current}'.", C.G)
                else: cprint("❌ Sai.", C.R)
            elif ch == "4":
                name = safe_input("Tên phiên cần xóa: ").strip()
                if name == "default": cprint("❌ Không thể xóa phiên mặc định.", C.R)
                elif self.sess_mgr.delete(name): cprint(f"✅ Đã xóa phiên '{name}'.", C.G)
                else: cprint("❌ Phiên không tồn tại.", C.R)
            elif ch == "5":
                fname = self.sess.export_chat(f"session_{self.sess_mgr.current}.txt")
                cprint(f"✅ Đã lưu {fname}", C.G)
            elif ch == "6": break
            else: cprint("❌ Sai.", C.R)

    def _add_to_favorites(self):
        model = self.cfg.data["model"]
        favs = self.cfg.data.setdefault("favorites", [])
        if model not in favs:
            favs.append(model); self.cfg.save()
            cprint(f"⭐ Đã thêm {model} vào yêu thích.", C.G)
        else: cprint("ℹ️ Model đã có trong danh sách yêu thích.", C.Y)

    def _list_favorites(self):
        favs = self.cfg.data.get("favorites", [])
        if not favs: cprint("ℹ️ Chưa có model yêu thích nào.", C.Y)
        else:
            cprint("⭐ Model yêu thích:", C.G)
            for m in favs: cprint(f"  - {m}", C.W)

    def _search_model(self, parts):
        if len(parts)<2: cprint("❌ /search <từ khóa>", C.R); return
        keyword = parts[1].lower()
        results = []
        for pkey, pdata in PROVIDERS.items():
            for m in pdata["models"]:
                if keyword in m["name"].lower():
                    results.append((pdata["name"], m))
        if results:
            cprint(f"🔍 Kết quả cho '{keyword}':", C.M)
            for prov_name, m in results:
                cprint(f"  [{prov_name}] {m['name']} ({m['type']}/{m['tier']}) Giá: {m.get('pricing','?')} - {m['desc']}", C.W)
        else: cprint("❌ Không tìm thấy model nào.", C.R)

    def run(self):
        cprint("\n✨ Ultimate AI Python v9.0 – Tất cả model + Hiển thị giá", C.CY+C.BOLD)
        self._main_menu()

if __name__ == "__main__":
    UltimateBot().run()
