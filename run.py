#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  🚀 ULTIMATE AI CHAT WEB – AUTO LAUNCHER v3.0           ║
║  Tự động cài đặt, khởi động server, tạo public link     ║
║  Ưu tiên localhost.run → Cloudflare Tunnel → ngrok      ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, time, re, signal, atexit, shutil, urllib.request

PORT = int(os.environ.get("PORT", 5000))
SERVER_FILE = "server.py"
INDEX_FILE = "index.html"

# ═══════════════════════════════════════════════
# 1. TIỆN ÍCH CƠ BẢN
# ═══════════════════════════════════════════════
def cmd(command, shell=False):
    """Chạy lệnh shell, trả về stdout (str) hoặc None nếu lỗi."""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return None

def find_executable(name):
    """Tìm đường dẫn của một chương trình trong PATH."""
    return shutil.which(name)

def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║   🚀 ULTIMATE AI CHAT WEB – AUTO LAUNCHER  ║
║   Ưu tiên localhost.run, dễ dàng public    ║
╚══════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════
# 2. KIỂM TRA & CÀI ĐẶT MÔI TRƯỜNG
# ═══════════════════════════════════════════════
def check_python():
    """Đảm bảo Python 3.8+."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 trở lên là bắt buộc.")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")

def ensure_pip():
    """Cài đặt pip nếu chưa có."""
    if cmd([sys.executable, "-m", "pip", "--version"]) is None:
        print("📦 Đang cài đặt pip...")
        if sys.platform == "linux":
            subprocess.run(["sudo", "apt", "update", "-qq"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt", "install", "-y", "python3-pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ pip sẵn sàng")

def install_packages():
    """Cài đặt các gói Python cần thiết."""
    required = ["flask", "flask-cors", "requests"]
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Đang cài {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Tất cả gói Python đã sẵn sàng")

def check_files():
    """Đảm bảo server.py và index.html tồn tại."""
    if not os.path.exists(SERVER_FILE):
        print(f"❌ Không tìm thấy {SERVER_FILE}. Hãy đặt file này cùng thư mục với run.py")
        sys.exit(1)
    if not os.path.exists(INDEX_FILE):
        print(f"⚠️  {INDEX_FILE} chưa có, tạo file mặc định...")
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"><title>AI Chat</title></head>
<body style="background:#0f0f1a;color:#eaeaea;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
  <div style="text-align:center"><h1>🚀 AI Chat Web</h1><p>Server đang chạy.</p></div>
</body>
</html>""")
    print("✅ File server & giao diện đã sẵn sàng")

# ═══════════════════════════════════════════════
# 3. KHỞI ĐỘNG SERVER
# ═══════════════════════════════════════════════
def start_server():
    """Khởi động Flask server và trả về process."""
    print(f"🌐 Khởi động server trên cổng {PORT}...")
    env = os.environ.copy()
    env["PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, SERVER_FILE],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # chờ server sẵn sàng
    if proc.poll() is not None:
        print(f"❌ Server không khởi động được:\n{proc.stderr.read().decode()}")
        sys.exit(1)
    print("✅ Server đang chạy")
    return proc

# ═══════════════════════════════════════════════
# 4. PUBLIC TUNNEL (ƯU TIÊN localhost.run)
# ═══════════════════════════════════════════════
def try_localhost_run():
    """Tạo tunnel qua localhost.run bằng SSH."""
    ssh = find_executable("ssh")
    if not ssh:
        print("❌ Không tìm thấy SSH client. Hãy cài đặt openssh-client.")
        return None

    print("🔗 Đang tạo tunnel qua localhost.run (SSH)...")
    try:
        # Lệnh SSH forward cổng 80 của remote về localhost:PORT
        proc = subprocess.Popen(
            [ssh, "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-R", f"80:localhost:{PORT}", "localhost.run"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  # gộp stderr vào stdout
            text=True
        )
        # Đọc từng dòng đầu ra để tìm URL
        for _ in range(60):
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            # In ra để người dùng thấy tiến trình
            print(line, end="")
            # Tìm URL dạng https://xxxx.lhr.life
            match = re.search(r'https://[a-zA-Z0-9.-]+\.lhr\.life', line)
            if match:
                url = match.group(0)
                print(f"\n🎉 Public URL: {url}")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ Lỗi localhost.run: {e}")
    return None

def download_cloudflared():
    """Tải cloudflared về thư mục hiện tại."""
    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    try:
        print("📥 Đang tải cloudflared...")
        urllib.request.urlretrieve(url, "./cloudflared")
        os.chmod("./cloudflared", 0o755)
        return "./cloudflared"
    except Exception as e:
        print(f"❌ Không thể tải cloudflared: {e}")
        return None

def try_cloudflare_tunnel():
    """Tạo tunnel qua Cloudflare Tunnel."""
    cf = find_executable("cloudflared")
    if not cf:
        cf = download_cloudflared()
        if not cf:
            return None

    print("🔗 Đang tạo Cloudflare Tunnel...")
    try:
        proc = subprocess.Popen(
            [cf, "tunnel", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        # Cloudflared in URL ra stderr
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
    """Tạo tunnel qua ngrok (nếu đã cài)."""
    ngrok = find_executable("ngrok")
    if not ngrok:
        return None
    print("🔗 Đang tạo ngrok tunnel...")
    try:
        proc = subprocess.Popen(
            [ngrok, "http", str(PORT), "--log=stdout"],
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
    """
    Thử tạo public tunnel theo thứ tự:
    1. localhost.run (SSH)
    2. Cloudflare Tunnel (tự tải nếu cần)
    3. ngrok (nếu có sẵn)
    """
    print("\n🔗 Đang tạo public URL...")

    # 1. localhost.run
    result = try_localhost_run()
    if result:
        return result

    print("⚠️  localhost.run không khả dụng, thử phương án khác...")

    # 2. Cloudflare Tunnel
    result = try_cloudflare_tunnel()
    if result:
        return result

    # 3. ngrok
    result = try_ngrok()
    if result:
        return result

    print("\n❌ Không thể tạo tunnel tự động.")
    print(f"   Server vẫn chạy tại http://localhost:{PORT}")
    print("   Bạn có thể tạo tunnel thủ công:")
    print(f"   - ssh -R 80:localhost:{PORT} localhost.run")
    print(f"   - cloudflared tunnel --url http://localhost:{PORT}")
    return None, None

# ═══════════════════════════════════════════════
# 5. DỌN DẸP & MAIN
# ═══════════════════════════════════════════════
def cleanup(server_proc, tunnel_proc):
    """Dừng server và tunnel khi thoát."""
    print("\n🛑 Đang dừng các tiến trình...")
    if tunnel_proc:
        tunnel_proc.kill()
    if server_proc:
        server_proc.kill()
    print("👋 Tạm biệt!")

def main():
    print_banner()
    check_python()
    ensure_pip()
    install_packages()
    check_files()

    server_proc = start_server()

    tunnel_proc, url = create_tunnel()

    # Đăng ký cleanup khi thoát
    atexit.register(cleanup, server_proc, tunnel_proc)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

    print(f"\n✨ Server: http://localhost:{PORT}")
    if url:
        print(f"✨ Public: {url}")
    print("   Nhấn Ctrl+C để dừng.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(server_proc, tunnel_proc)

if __name__ == "__main__":
    main()
