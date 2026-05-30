#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Auto Launcher
- Cài đặt dependencies
- Khởi động server
- Tạo public URL qua cloudflared (với --idle-timeout 300s) hoặc serveo.net
"""

import os, sys, subprocess, time, re, signal, atexit, shutil, urllib.request

PORT = 5000
SERVER_FILE = "server.py"
INDEX_FILE = "index.html"

def cmd(command, shell=False):
    try:
        r = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    except:
        return None

def find_exe(name):
    return shutil.which(name)

def banner():
    print("""
╔══════════════════════════════════════════════╗
║  🚀 ULTIMATE AI CHAT – AUTO LAUNCHER       ║
╚══════════════════════════════════════════════╝
""")

def check_python():
    if sys.version_info < (3, 8): print("❌ Python 3.8+ required."); sys.exit(1)
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
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Packages ready")

def check_files():
    if not os.path.exists(SERVER_FILE):
        print(f"❌ {SERVER_FILE} not found."); sys.exit(1)
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w") as f: f.write("<html><body><h1>AI Chat</h1></body></html>")
    print("✅ Files ready")

def start_server():
    print(f"🌐 Starting server on port {PORT}...")
    env = os.environ.copy(); env["PORT"] = str(PORT)
    proc = subprocess.Popen([sys.executable, SERVER_FILE], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    time.sleep(3)
    if proc.poll() is not None:
        print(f"❌ Server failed:\n{proc.stderr.read().decode()}"); sys.exit(1)
    print("✅ Server running")
    return proc

def create_tunnel():
    # 1. Cloudflare Tunnel (with idle timeout)
    cf = find_exe("cloudflared")
    if not cf:
        print("📥 Downloading cloudflared...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        urllib.request.urlretrieve(url, "./cloudflared")
        os.chmod("./cloudflared", 0o755)
        cf = "./cloudflared"
    print("🔗 Creating Cloudflare Tunnel (idle‑timeout 300s)...")
    try:
        proc = subprocess.Popen(
            [cf, "tunnel", "--no-autoupdate", "--url", f"http://localhost:{PORT}", "--idle-timeout", "300s"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for _ in range(60):
            line = proc.stderr.readline()
            if not line: continue
            match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print(f"\n🎉 Public URL: {url}")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ Cloudflare error: {e}")

    # 2. Fallback: serveo.net
    print("Trying serveo.net...")
    ssh = find_exe("ssh")
    if ssh:
        key_file = os.path.expanduser("~/.ssh/id_rsa_serveo")
        if not os.path.exists(key_file):
            subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", key_file, "-N", "", "-q"], check=True)
        try:
            proc = subprocess.Popen([ssh, "-o", "StrictHostKeyChecking=no", "-i", key_file, "-R", f"80:localhost:{PORT}", "serveo.net"],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for _ in range(30):
                line = proc.stdout.readline()
                if not line: continue
                match = re.search(r'https://[a-zA-Z0-9-]+\.serveo\.net', line)
                if match:
                    url = match.group(0)
                    print(f"\n🎉 Public URL: {url}")
                    return proc, url
            proc.kill()
        except Exception as e:
            print(f"❌ serveo error: {e}")

    print("❌ Could not create tunnel.")
    return None, None

def cleanup(server, tunnel):
    print("\n🛑 Stopping...")
    if tunnel: tunnel.kill()
    if server: server.kill()
    print("👋 Goodbye!")

def main():
    banner()
    check_python()
    ensure_pip()
    install_packages()
    check_files()

    server_proc = start_server()
    tunnel_proc, url = create_tunnel()

    atexit.register(cleanup, server_proc, tunnel_proc)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

    print(f"\n✨ Local: http://localhost:{PORT}")
    if url: print(f"✨ Public: {url}")
    print("   Press Ctrl+C to stop.\n")

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: pass
    finally: cleanup(server_proc, tunnel_proc)

if __name__ == "__main__":
    main()
