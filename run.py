#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  🚀 ULTIMATE AI CHAT – AUTO LAUNCHER v4.0              ║
║  Tự động tạo public link qua serveo.net / cloudflared   ║
║  Fix lỗi 1033, Permission denied                        ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, time, re, signal, atexit, shutil, urllib.request, tempfile

PORT = 5000
SERVER_FILE = "server.py"
INDEX_FILE = "index.html"

# ═══════════════════════════════════════════════
# 1. TIỆN ÍCH
# ═══════════════════════════════════════════════
def cmd(command, shell=False):
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
║  🚀 ULTIMATE AI CHAT – AUTO PUBLIC LINK     ║
║  serveo.net / cloudflared / bore             ║
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
    if cmd([sys.executable, "-m", "pip", "--version"]) is None:
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
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Packages ready")

def check_files():
    if not os.path.exists(SERVER_FILE):
        print(f"❌ Missing {SERVER_FILE}"); sys.exit(1)
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"><title>AI Chat</title></head>
<body style="background:#0f0f1a;color:#eaeaea;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
<div style="text-align:center"><h1>🚀 AI Chat</h1><p>Server is running.</p></div>
</body>
</html>""")
    print("✅ Files ready")

# ═══════════════════════════════════════════════
# 3. START SERVER
# ═══════════════════════════════════════════════
def start_server():
    print(f"🌐 Starting server on port {PORT}...")
    env = os.environ.copy(); env["PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, SERVER_FILE], env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    # Chờ server sẵn sàng
    for _ in range(10):
        time.sleep(1)
        if proc.poll() is not None:
            print(f"❌ Server failed:\n{proc.stderr.read().decode()}")
            sys.exit(1)
        # Kiểm tra xem server đã listen chưa
        if cmd(["curl", "-s", f"http://localhost:{PORT}/api/models"]) is not None:
            break
    print("✅ Server running")
    return proc

# ═══════════════════════════════════════════════
# 4. TUNNEL SOLUTIONS (FIX LỖI THỰC TẾ)
# ═══════════════════════════════════════════════

def try_serveo():
    """Dùng serveo.net với SSH key tự động. Không cần publickey."""
    ssh = find_exe("ssh")
    if not ssh:
        print("❌ SSH not found.")
        return None

    # Tạo SSH key tạm nếu chưa có
    key_file = os.path.expanduser("~/.ssh/id_rsa_serveo")
    if not os.path.exists(key_file):
        print("🔑 Generating temporary SSH key...")
        os.makedirs(os.path.expanduser("~/.ssh"), exist_ok=True)
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", key_file, "-N", "", "-q"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Thêm vào ssh config để không bị Permission denied
        with open(os.path.expanduser("~/.ssh/config"), "a") as f:
            f.write(f"\nHost serveo.net\n  IdentityFile {key_file}\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n")

    print("🔗 Creating tunnel via serveo.net...")
    try:
        proc = subprocess.Popen(
            [ssh, "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-i", key_file,
             "-R", f"80:localhost:{PORT}", "serveo.net"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True
        )
        for _ in range(30):
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            print(line, end="")
            match = re.search(r'https://[a-zA-Z0-9-]+\.serveo\.net', line)
            if match:
                url = match.group(0)
                print(f"\n🎉 Public URL: {url}")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ serveo.net error: {e}")
    return None

def try_cloudflared_fixed():
    """Sửa lỗi 1033: đảm bảo cloudflared trỏ đúng localhost:PORT và server listen."""
    cf = find_exe("cloudflared")
    if not cf:
        print("📥 Downloading cloudflared...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        try:
            urllib.request.urlretrieve(url, "./cloudflared")
            os.chmod("./cloudflared", 0o755)
            cf = "./cloudflared"
        except Exception as e:
            print(f"❌ Cannot download: {e}")
            return None

    # Kiểm tra server đã sẵn sàng chưa
    print("🔍 Checking server connection...")
    for _ in range(5):
        if cmd(["curl", "-s", f"http://localhost:{PORT}/api/models"]) is not None:
            break
        time.sleep(1)
    else:
        print("❌ Server not responding. Cannot create tunnel.")
        return None

    print("🔗 Creating Cloudflare Tunnel...")
    try:
        proc = subprocess.Popen(
            [cf, "tunnel", "--no-autoupdate", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        for _ in range(60):
            line = proc.stderr.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print(f"\n🎉 Public URL: {url}")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ Cloudflare error: {e}")
    return None

def try_bore():
    """Dùng bore.pub - đơn giản, không cần xác thực."""
    bore = find_exe("bore")
    if not bore:
        # Tải bore binary
        print("📥 Downloading bore...")
        url = "https://github.com/ekzhang/bore/releases/download/v0.5.0/bore-v0.5.0-x86_64-unknown-linux-musl.tar.gz"
        try:
            urllib.request.urlretrieve(url, "./bore.tar.gz")
            subprocess.run(["tar", "-xzf", "./bore.tar.gz"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            bore = "./bore"
            os.chmod(bore, 0o755)
        except Exception as e:
            print(f"❌ Cannot download bore: {e}")
            return None

    print("🔗 Creating tunnel via bore.pub...")
    try:
        proc = subprocess.Popen(
            [bore, "local", str(PORT), "--to", "bore.pub"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True
        )
        for _ in range(30):
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            print(line, end="")
            match = re.search(r'listening at (\S+)', line)
            if match:
                host = match.group(1)
                url = f"http://{host}"
                print(f"\n🎉 Public URL: {url}")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ bore error: {e}")
    return None

def create_tunnel():
    """Thử lần lượt: serveo.net → cloudflared → bore."""
    print("\n🔗 Creating public URL...")

    # 1. serveo.net (SSH, tự động key)
    print("[1/3] serveo.net...")
    result = try_serveo()
    if result:
        return result

    # 2. cloudflared (đã fix)
    print("\n[2/3] Cloudflare Tunnel...")
    result = try_cloudflared_fixed()
    if result:
        return result

    # 3. bore.pub
    print("\n[3/3] bore.pub...")
    result = try_bore()
    if result:
        return result

    print("\n❌ Could not create tunnel.")
    print(f"   Server is at http://localhost:{PORT}")
    return None, None

# ═══════════════════════════════════════════════
# 5. MAIN
# ═══════════════════════════════════════════════
def cleanup(server, tunnel):
    print("\n🛑 Stopping...")
    if tunnel: tunnel.kill()
    if server: server.kill()
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
