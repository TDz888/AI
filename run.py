#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Auto Launcher (Fixed)
- Cài đặt dependencies
- Khởi động server Flask
- Tạo public URL qua Cloudflare Tunnel (có idle‑timeout) hoặc serveo.net
"""

import os, sys, subprocess, time, re, signal, atexit, shutil, urllib.request

PORT = 5000
SERVER_FILE = "server.py"
INDEX_FILE = "index.html"

# ═══════════════════════════════════════════════
# 1. TIỆN ÍCH
# ═══════════════════════════════════════════════
def run_cmd(command, shell=False):
    """Chạy lệnh shell, trả về stdout hoặc None."""
    try:
        r = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    except:
        return None

def find_exe(name):
    return shutil.which(name)

def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║  🚀 ULTIMATE AI CHAT – AUTO LAUNCHER       ║
╚══════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════
# 2. KIỂM TRA MÔI TRƯỜNG
# ═══════════════════════════════════════════════
def check_python():
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required."); sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")

def ensure_pip():
    if run_cmd([sys.executable, "-m", "pip", "--version"]) is None:
        print("📦 Installing pip...")
        if sys.platform == "linux":
            subprocess.run(["sudo", "apt", "update", "-qq"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt", "install", "-y", "python3-pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ pip ready")

def install_packages():
    for pkg in ["flask", "flask-cors", "requests"]:
        try:
            __import__(pkg.replace("-","_"))
        except ImportError:
            print(f"📦 Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Packages ready")

def check_files():
    if not os.path.exists(SERVER_FILE):
        print(f"❌ {SERVER_FILE} not found in current directory."); sys.exit(1)
    if not os.path.exists(INDEX_FILE):
        print(f"⚠️  {INDEX_FILE} not found. Creating a default one...")
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><title>AI Chat</title></head><body style="background:#0f0f1a;color:#eaeaea;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;"><div style="text-align:center"><h1>🚀 AI Chat</h1><p>Server is running.</p></div></body></html>""")
    print("✅ Files ready")

# ═══════════════════════════════════════════════
# 3. START SERVER
# ═══════════════════════════════════════════════
def start_server():
    print(f"🌐 Starting Flask server on port {PORT}...")
    env = os.environ.copy()
    env["PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, SERVER_FILE],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE
    )
    # Chờ server sẵn sàng
    for _ in range(10):
        time.sleep(1)
        if proc.poll() is not None:
            print(f"❌ Server failed to start:\n{proc.stderr.read().decode()}")
            sys.exit(1)
        # Kiểm tra xem server đã listen chưa
        if run_cmd(["curl", "-s", f"http://localhost:{PORT}/api/models"]) is not None:
            break
    print("✅ Server is running")
    return proc

# ═══════════════════════════════════════════════
# 4. TUNNEL
# ═══════════════════════════════════════════════
def try_cloudflare_tunnel():
    """Tải cloudflared nếu cần và tạo tunnel. Trả về (process, url) hoặc None."""
    cf = find_exe("cloudflared")
    if not cf:
        print("📥 Downloading cloudflared...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        try:
            urllib.request.urlretrieve(url, "./cloudflared")
            os.chmod("./cloudflared", 0o755)
            cf = "./cloudflared"
        except Exception as e:
            print(f"❌ Cannot download cloudflared: {e}")
            return None

    print("🔗 Starting Cloudflare Tunnel (idle‑timeout 300s)...")
    try:
        proc = subprocess.Popen(
            [cf, "tunnel", "--no-autoupdate", "--url", f"http://localhost:{PORT}", "--idle-timeout", "300s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Đọc stderr để tìm URL (cloudflared in ra stderr)
        start_time = time.time()
        while time.time() - start_time < 60:
            line = proc.stderr.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            # In ra để debug
            print(f"   {line.strip()}")
            match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print(f"\n🎉 PUBLIC URL: {url}")
                return proc, url
        proc.kill()
        print("⚠️  Cloudflare Tunnel did not return a URL in time.")
    except Exception as e:
        print(f"❌ Cloudflare Tunnel error: {e}")
    return None

def try_serveo():
    """Tạo tunnel qua serveo.net bằng SSH. Trả về (process, url) hoặc None."""
    ssh = find_exe("ssh")
    if not ssh:
        print("❌ SSH not found. Cannot use serveo.net.")
        return None

    # Tạo SSH key tạm nếu chưa có
    key_file = os.path.expanduser("~/.ssh/id_rsa_serveo")
    if not os.path.exists(key_file):
        print("🔑 Generating temporary SSH key for serveo.net...")
        os.makedirs(os.path.expanduser("~/.ssh"), exist_ok=True)
        subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", key_file, "-N", "", "-q"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    print("🔗 Starting serveo.net tunnel...")
    try:
        proc = subprocess.Popen(
            [ssh, "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-i", key_file, "-R", f"80:localhost:{PORT}", "serveo.net"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        start_time = time.time()
        while time.time() - start_time < 45:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            print(f"   {line.strip()}")
            match = re.search(r'https://[a-zA-Z0-9-]+\.serveo\.net', line)
            if match:
                url = match.group(0)
                print(f"\n🎉 PUBLIC URL: {url}")
                return proc, url
        proc.kill()
        print("⚠️  serveo.net did not return a URL in time.")
    except Exception as e:
        print(f"❌ serveo.net error: {e}")
    return None

def create_tunnel():
    """Thử tạo tunnel, ưu tiên Cloudflare, fallback serveo."""
    print("\n🔗 Creating public URL...")

    # 1. Cloudflare Tunnel
    print("[1] Trying Cloudflare Tunnel...")
    result = try_cloudflare_tunnel()
    if result:
        return result

    # 2. serveo.net
    print("[2] Trying serveo.net...")
    result = try_serveo()
    if result:
        return result

    print("\n❌ Could not create any tunnel.")
    print(f"   ➡️  Your server is running at http://localhost:{PORT}")
    print("   ➡️  To expose it manually, run one of these:")
    print(f"       cloudflared tunnel --url http://localhost:{PORT}")
    print(f"       ssh -R 80:localhost:{PORT} serveo.net")
    return None, None

# ═══════════════════════════════════════════════
# 5. MAIN
# ═══════════════════════════════════════════════
def cleanup(server_proc, tunnel_proc):
    print("\n🛑 Shutting down...")
    if tunnel_proc:
        tunnel_proc.kill()
    if server_proc:
        server_proc.kill()
    print("👋 Goodbye!")

def main():
    print_banner()
    check_python()
    ensure_pip()
    install_packages()
    check_files()

    server_proc = start_server()

    tunnel_proc, url = create_tunnel()

    atexit.register(cleanup, server_proc, tunnel_proc)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

    print(f"\n✨ Local: http://localhost:{PORT}")
    if url:
        print(f"✨ Public: {url}")
    print("   Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(server_proc, tunnel_proc)

if __name__ == "__main__":
    main()
