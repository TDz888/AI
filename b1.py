#!/usr/bin/env python3
"""
🚀 ULTIMATE TELEGRAM AI AGENT BOT
- Đa mô hình AI (hơn 50 model)
- GitHub tích hợp: tạo repo, push file, tự động code
- Text-to-Speech (TTS) gửi file MP3
- Gửi file TXT nếu phản hồi quá dài
- Quản lý hội thoại thông minh
"""

import logging, requests, json, io, base64, os, tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ═══════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = "8909561772:AAGQgxrbvXbi-RACF4_Z7iiS4R7NA6Za6wU"
AI_API_BASE = "https://ckey.vn/v1/chat/completions"
AI_API_KEY = "sk-e317a237354192e26f99951f06e4882779e8a0e08e86d2f71242e8ff770bdf24"
TTS_API = "https://ckey.vn/v1/audio/speech"
GITHUB_TOKEN = "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"
DEFAULT_MODEL = "🚀 GLM4.7"
SYSTEM_PROMPT = "You are a helpful, intelligent AI assistant. Respond concisely."

AVAILABLE_MODELS = {
    "💎 Gemini Embedding 2": "gemini-embedding-2-preview",
    "🚀 GLM4.7": "glm4.7",
    "👨‍💻 Qwen3 Coder 480B": "qwen3-coder-480b-a35b-instruct",
    "⚡ Mistral Medium 3.5": "mistral-medium-3.5-128b",
    "🧠 Mistral Small 4": "mistral-small-4-119b-2603",
    "🔥 DeepSeek V3 (DeepSeek-3.2)": "deepseek-3.2",
    "🐬 DeepSeek R1 Distill Qwen": "deepseek-r1-distill-qwen-32b",
    "🦙 Llama Nemotron Embed": "llama-nemotron-embed-vl-1b-v2",
    "🇻🇳 ViTTS HoaiMy": "google-tts/vi",
    "🏆 Mistral Large 3 (ChieuStudio)": "chieustudio/mistral-large-3-675b-instruct-2512",
    "🤖 DeepSeek R1 (ChieuStudio)": "chieustudio/deepseek-r1",
    "🌟 MiniMax M2.7": "namtran96hth/MiniMax-M2.7",
    "📝 Text Embedding 3 Small": "text-embedding-3-small",
    "🚀 Qwen3 Coder Next": "qwen3-coder-next",
    "💎 MiniMax M2.5": "minimax-m2.5",
    "💎 MiniMax M2.1": "minimax-m2.1",
    "🏆 Mistral Large 3 (Official)": "mistral-large-3-675b-instruct-2512",
    "⚡ DeepSeek V4 Flash": "deepseek-v4-flash",
    "⚡ DeepSeek V4 Flash (Vyke)": "vykelongthuong/Deepseek V4 Flash",
    "🤖 Kimi K2.5": "kimi-k2.5",
    "🐉 GLM-5": "glm-5",
    "🤖 Kimi K2.6": "kimi-k2.6",
    "🤔 Grok 4.20 Thinking": "grok-4.20-thinking",
    "🤖 Grok 4.3": "grok-4.3",
    "⚡ Grok 4.20 Fast": "grok-4.20-fast",
    "🤖 GPT-5.4 Mini": "gpt-5.4-mini",
    "🐉 GLM-5.1": "glm-5.1",
    "🤖 Claude Haiku 4.5": "claude-haiku-4.5",
    "🤖 GPT-5.2": "gpt-5.2",
    "🤖 GPT-5.3 Codex": "gpt-5.3-codex",
    "🤖 GPT-5.3 Codex High": "gpt-5.3-codex-high",
    "🤖 GPT-5.4": "gpt-5.4",
    "🤖 Claude Sonnet 4.6": "claude-sonnet-4.6",
    "🤖 Claude Sonnet 4.5": "claude-sonnet-4.5",
    "🤖 Qwen 3.7 Max": "phuocanh421994/Qwen 3.7 max",
    "🤖 GPT-5.5 (Vyke)": "vykelongthuong/GPT 5.5",
    "🤖 GPT-5.5 (W3leee)": "w3leee/GPT 5.5",
}

# ═══════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# GITHUB CLIENT
# ═══════════════════════════════════════════════
class GitHubClient:
    def __init__(self, token, owner=None, repo=None, branch="main"):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _base(self):
        return f"https://api.github.com/repos/{self.owner}/{self.repo}"

    def create_repo(self, name, private=False):
        url = "https://api.github.com/user/repos"
        payload = {"name": name, "private": private, "auto_init": True}
        resp = requests.post(url, headers=self.headers, json=payload)
        if resp.status_code == 201:
            self.owner = resp.json()["owner"]["login"]
            self.repo = name
            return True, f"Đã tạo repo {name} (owner: {self.owner})"
        return False, resp.json()

    def push(self, path, content, msg="Auto-commit by Telegram Bot"):
        url = f"{self._base()}/contents/{path}"
        sha = self._get_sha(path)
        payload = {"message": msg, "content": base64.b64encode(content.encode()).decode(), "branch": self.branch}
        if sha: payload["sha"] = sha
        resp = requests.put(url, headers=self.headers, json=payload)
        if resp.status_code in (200, 201):
            return True, resp.json()["content"]["html_url"]
        return False, resp.json()

    def get(self, path):
        url = f"{self._base()}/contents/{path}?ref={self.branch}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return True, base64.b64decode(resp.json()["content"]).decode()
        return False, resp.json()

    def list(self, path=""):
        url = f"{self._base()}/contents/{path}?ref={self.branch}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return True, [f["name"] for f in resp.json()]
        return False, resp.json()

    def delete(self, path, msg="Deleted by Telegram Bot"):
        url = f"{self._base()}/contents/{path}"
        sha = self._get_sha(path)
        if not sha: return False, "File không tồn tại"
        payload = {"message": msg, "sha": sha, "branch": self.branch}
        resp = requests.delete(url, headers=self.headers, json=payload)
        return (True, "Đã xóa") if resp.status_code == 200 else (False, resp.json())

    def _get_sha(self, path):
        url = f"{self._base()}/contents/{path}?ref={self.branch}"
        resp = requests.get(url, headers=self.headers)
        return resp.json()["sha"] if resp.status_code == 200 else None

# ═══════════════════════════════════════════════
# USER STATE MANAGEMENT
# ═══════════════════════════════════════════════
user_states = {}

def get_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = {
            'history': [],
            'model': DEFAULT_MODEL,
            'gh_owner': None,
            'gh_repo': None,
            'last_message': None
        }
    return user_states[user_id]

# ═══════════════════════════════════════════════
# HELPER: GỌI API CHAT
# ═══════════════════════════════════════════════
def call_ai(model_id, messages, max_tokens=2048):
    headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages": messages, "temperature": 0.7, "max_tokens": max_tokens, "stream": False}
    try:
        resp = requests.post(AI_API_BASE, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        return None
    except Exception as e:
        logger.error(f"API error: {e}")
        raise

# ═══════════════════════════════════════════════
# HELPER: GỬI TIN NHẮN DÀI
# ═══════════════════════════════════════════════
async def send_long_message(update, text, parse_mode='Markdown'):
    if len(text) <= 4000:
        await update.message.reply_text(text, parse_mode=parse_mode)
    else:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            filepath = f.name
        await update.message.reply_document(document=open(filepath, 'rb'), filename="response.txt")
        os.unlink(filepath)

# ═══════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    await update.message.reply_text(
        f"🤖 *Ultimate AI Agent Bot*\n"
        f"Model: *{state['model']}*\n\n"
        f"📂 /models - Danh sách model\n"
        f"🔄 /switch <số> - Đổi model\n"
        f"🗑 /reset - Xóa lịch sử\n"
        f"🔊 /tts <text> - Chuyển văn bản thành giọng nói\n"
        f"🐙 /git help - Các lệnh GitHub\n"
        f"💬 Nhắn tin trực tiếp để chat!",
        parse_mode='Markdown'
    )

async def models_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    keys = list(AVAILABLE_MODELS.keys())
    msg = "📂 *Danh sách Model*\n"
    for i, k in enumerate(keys, 1):
        marker = "✅" if k == state['model'] else "⚪"
        msg += f"*{i}.* {marker} {k}\n"
    msg += "\n👉 `/switch <số>` để đổi model"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Dùng: `/switch <số>`", parse_mode='Markdown')
        return
    try:
        idx = int(context.args[0])
        keys = list(AVAILABLE_MODELS.keys())
        if 1 <= idx <= len(keys):
            state = get_state(update.effective_user.id)
            state['model'] = keys[idx-1]
            await update.message.reply_text(f"✅ Đã chọn: *{keys[idx-1]}*", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Số từ 1 đến {len(keys)}", parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("❌ Số không hợp lệ", parse_mode='Markdown')

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    state['history'] = []
    await update.message.reply_text("🗑 Đã xóa lịch sử chat.")

async def tts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(update.effective_user.id)
    text = ' '.join(context.args) if context.args else state.get('last_message')
    if not text:
        await update.message.reply_text("❌ Cần văn bản. Dùng: `/tts <text>` hoặc chat trước.", parse_mode='Markdown')
        return
    await context.bot.send_chat_action(update.effective_chat.id, "record_voice")
    try:
        headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "vi-VN-NamMinhNeural", "input": text, "voice": "NamMinh"}
        resp = requests.post(TTS_API, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        audio = io.BytesIO(resp.content)
        audio.name = "speech.mp3"
        await update.message.reply_voice(audio)
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi TTS: {e}")

# ═══════════════════════════════════════════════
# GITHUB COMMANDS
# ═══════════════════════════════════════════════
async def git_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🐙 *GitHub Commands:*\n"
            "/git config <owner> <repo> - Thiết lập repo\n"
            "/git create <tên> - Tạo repo mới\n"
            "/git push <path> <nội dung> - Push file\n"
            "/git list - Danh sách file\n"
            "/git get <path> - Xem file\n"
            "/git delete <path> - Xóa file\n"
            "/git auto <yêu cầu> - AI tự code và push",
            parse_mode='Markdown'
        )
        return
    state = get_state(update.effective_user.id)
    gh = GitHubClient(GITHUB_TOKEN, state.get('gh_owner'), state.get('gh_repo'))
    action = context.args[0].lower()
    if action == 'config':
        if len(context.args) >= 3:
            state['gh_owner'] = context.args[1]
            state['gh_repo'] = context.args[2]
            await update.message.reply_text(f"✅ Đã lưu GitHub: {state['gh_owner']}/{state['gh_repo']}")
        else:
            await update.message.reply_text("❌ Dùng: /git config <owner> <repo>")
    elif action == 'create':
        if len(context.args) >= 2:
            name = context.args[1]
            ok, msg = gh.create_repo(name)
            if ok:
                state['gh_owner'] = gh.owner
                state['gh_repo'] = gh.repo
                await update.message.reply_text(f"✅ {msg}")
            else:
                await update.message.reply_text(f"❌ {msg}")
        else:
            await update.message.reply_text("❌ Dùng: /git create <tên>")
    elif action in ('push', 'get', 'delete', 'list'):
        if not state.get('gh_owner') or not state.get('gh_repo'):
            await update.message.reply_text("❌ Chưa cấu hình GitHub. Dùng: /git config <owner> <repo>")
            return
        if action == 'push':
            if len(context.args) >= 3:
                path = context.args[1]
                content = ' '.join(context.args[2:])
                ok, msg = gh.push(path, content)
                await update.message.reply_text(f"{'✅' if ok else '❌'} {msg}" if ok else f"❌ {msg}")
            else:
                await update.message.reply_text("❌ Dùng: /git push <path> <nội dung>")
        elif action == 'list':
            ok, files = gh.list()
            if ok:
                await update.message.reply_text("📁 " + "\n".join(files) if files else "Repo trống")
            else:
                await update.message.reply_text(f"❌ {files}")
        elif action == 'get':
            if len(context.args) >= 2:
                ok, content = gh.get(context.args[1])
                if ok:
                    await send_long_message(update, f"📄 *{context.args[1]}*\n```\n{content}\n```")
                else:
                    await update.message.reply_text(f"❌ {content}")
            else:
                await update.message.reply_text("❌ Dùng: /git get <path>")
        elif action == 'delete':
            if len(context.args) >= 2:
                ok, msg = gh.delete(context.args[1])
                await update.message.reply_text(f"{'✅' if ok else '❌'} {msg}")
            else:
                await update.message.reply_text("❌ Dùng: /git delete <path>")
    elif action == 'auto':
        if not state.get('gh_owner') or not state.get('gh_repo'):
            await update.message.reply_text("❌ Chưa cấu hình GitHub.")
            return
        task = ' '.join(context.args[1:])
        if not task:
            await update.message.reply_text("❌ Mô tả yêu cầu: /git auto <yêu cầu>")
            return
        await context.bot.send_chat_action(update.effective_chat.id, "typing")
        try:
            # Gọi AI để sinh code
            msgs = [
                {"role": "system", "content": "You are a coding assistant. Generate code based on the user's request. Wrap code in ```language ... ``` blocks. Keep it short and functional."},
                {"role": "user", "content": task}
            ]
            ai_resp = call_ai(AVAILABLE_MODELS[state['model']], msgs, max_tokens=1024)
            if ai_resp:
                # Tìm block code
                import re
                code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', ai_resp, re.DOTALL)
                if code_blocks:
                    code = code_blocks[0]
                    path = f"auto_{int(time.time())}.py"  # Tự đặt tên
                    ok, msg = gh.push(path, code, f"Auto-generated: {task}")
                    if ok:
                        await update.message.reply_text(f"✅ Đã push `{path}`: {msg}", parse_mode='Markdown')
                    else:
                        await update.message.reply_text(f"❌ Push lỗi: {msg}")
                else:
                    await update.message.reply_text("❌ AI không tạo code block.")
            else:
                await update.message.reply_text("❌ AI không phản hồi.")
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi: {e}")
    else:
        await update.message.reply_text("❓ Lệnh không rõ. /git help")

# ═══════════════════════════════════════════════
# HANDLE MESSAGE
# ═══════════════════════════════════════════════
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = update.effective_user.id
    text = update.message.text
    state = get_state(user_id)
    state['last_message'] = text
    model_id = AVAILABLE_MODELS.get(state['model'], AVAILABLE_MODELS[DEFAULT_MODEL])

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    # Lưu vào history
    state['history'].append({"role": "user", "content": text})
    if len(state['history']) > 20:
        state['history'] = state['history'][-20:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + state['history']
    try:
        ai_response = call_ai(model_id, messages)
        if ai_response:
            state['history'].append({"role": "assistant", "content": ai_response})
            await send_long_message(update, f"🤖 *{state['model']}*\n{ai_response}")
        else:
            await update.message.reply_text("❌ Không nhận được phản hồi.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi: {e}")

# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('models', models_cmd))
    app.add_handler(CommandHandler('switch', switch))
    app.add_handler(CommandHandler('reset', reset))
    app.add_handler(CommandHandler('tts', tts_cmd))
    app.add_handler(CommandHandler('git', git_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🚀 Bot đang chạy...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
