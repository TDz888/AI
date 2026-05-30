#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Auto Launcher v2.1
Ưu tiên localhost.run, Cloudflare Tunnel & ngrok dự phòng
"""

import os, sys, subprocess, time, re, shutil, urllib.request, signal, atexit

PORT = int(os.environ.get("PORT", 5000))
SERVER_FILE = "server.py"

# ==================== UTILITIES ====================
def cmd(command, shell=False):
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return None

def find_executable(name):
    return shutil.which(name)

def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║   🚀 ULTIMATE AI CHAT WEB – AUTO LAUNCHER  ║
║   Ưu tiên localhost.run (SSH)              ║
╚══════════════════════════════════════════════╝
""")

def check_python():
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required."); sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")

def install_pip():
    if cmd([sys.executable, "-m", "pip", "--version"]) is None:
        print("📦 Installing pip...")
        if sys.platform == "linux":
            subprocess.run(["sudo", "apt", "update", "-qq"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt", "install", "-y", "python3-pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
    print("✅ pip ready")

def install_packages():
    for pkg in ["flask", "flask-cors", "requests"]:
        try:
            __import__(pkg.replace("-","_"))
        except ImportError:
            print(f"📦 Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ All packages installed")

# ==================== SERVER ====================
def start_server():
    print(f"🌐 Starting server on port {PORT}...")
    env = os.environ.copy(); env["PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, SERVER_FILE], env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(3)
    if proc.poll() is not None:
        print(f"❌ Server failed to start:\n{proc.stderr.read().decode()}")
        sys.exit(1)
    print("✅ Server running")
    return proc

# ==================== TUNNEL ====================
def try_localhost_run():
    """Dùng SSH để tạo tunnel qua localhost.run (không cần cài gì)."""
    if not find_executable("ssh"):
        print("❌ Không tìm thấy SSH client.")
        return None
    print("🔗 Đang tạo tunnel qua localhost.run...")
    try:
        proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-R", f"80:localhost:{PORT}", "localhost.run"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        # Đọc URL từ stdout
        for _ in range(60):
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            # In ra để người dùng thấy tiến trình
            print(line, end="")
            if "https://" in line and ".lhr.life" in line:
                url = line.strip()
                print(f"\n🎉 Public URL: {url}")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ Lỗi localhost.run: {e}")
    return None

def try_cloudflare_tunnel():
    """Tải cloudflared nếu chưa có, sau đó tạo tunnel."""
    cf_path = find_executable("cloudflared")
    if not cf_path:
        print("📥 Đang tải cloudflared...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        try:
            urllib.request.urlretrieve(url, "./cloudflared")
            os.chmod("./cloudflared", 0o755)
            cf_path = "./cloudflared"
        except Exception as e:
            print(f"❌ Không thể tải cloudflared: {e}")
            return None
    print("🔗 Đang tạo Cloudflare Tunnel...")
    try:
        proc = subprocess.Popen(
            [cf_path, "tunnel", "--url", f"http://localhost:{PORT}"],
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
        print(f"❌ Lỗi Cloudflare Tunnel: {e}")
    return None

def try_ngrok():
    ngrok_path = find_executable("ngrok")
    if not ngrok_path:
        return None
    print("🔗 Đang tạo ngrok tunnel...")
    try:
        proc = subprocess.Popen(
            [ngrok_path, "http", str(PORT), "--log=stdout"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        for _ in range(30):
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            match = re.search(r'url=(https://[^\s]+)', line)
            if match:
                url = match.group(1)
                print(f"\n🎉 Public URL: {url}")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ Lỗi ngrok: {e}")
    return None

def create_tunnel():
    """Thử các phương thức theo thứ tự: localhost.run → Cloudflare → ngrok."""
    print("\n🔗 Đang tạo public URL...")

    # 1. localhost.run (không cần cài đặt gì, ổn định)
    result = try_localhost_run()
    if result:
        return result

    # 2. Cloudflare Tunnel (cần tải cloudflared)
    result = try_cloudflare_tunnel()
    if result:
        return result

    # 3. ngrok (nếu đã cài)
    result = try_ngrok()
    if result:
        return result

    print("\n❌ Không thể tạo tunnel tự động.")
    print(f"   Server đang chạy tại http://localhost:{PORT}")
    print("   Hãy thử thủ công:")
    print(f"   - ssh -R 80:localhost:{PORT} localhost.run")
    print(f"   - cloudflared tunnel --url http://localhost:{PORT}")
    return None, None

# ==================== MAIN ====================
def cleanup(server_proc, tunnel_proc):
    print("\n🛑 Đang dừng...")
    if tunnel_proc: tunnel_proc.kill()
    if server_proc: server_proc.kill()
    print("👋 Tạm biệt!")

def main():
    print_banner()
    check_python()
    install_pip()
    install_packages()

    if not os.path.exists(SERVER_FILE):
        print(f"❌ Không tìm thấy {SERVER_FILE}")
        sys.exit(1)

    server_proc = start_server()
    tunnel_proc, url = create_tunnel()

    atexit.register(cleanup, server_proc, tunnel_proc)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

    print(f"\n✨ Server: http://localhost:{PORT}")
    if url:
        print(f"✨ Public: {url}")
    print("   Nhấn Ctrl+C để thoát.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(server_proc, tunnel_proc)

if __name__ == "__main__":
    main()
