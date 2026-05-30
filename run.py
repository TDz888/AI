#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  🚀 ULTIMATE AI CHAT WEB – AUTO LAUNCHER v2.0           ║
║  Tự động cài đặt môi trường, khởi động server & tunnel  ║
║  Hỗ trợ Cloudflare Tunnel, localhost.run, ngrok          ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, time, platform, signal, atexit, re, json, shutil, urllib.request

# ==================== CONFIGURATION ====================
PORT = int(os.environ.get("PORT", 5000))
SERVER_FILE = "server.py"
INDEX_FILE = "index.html"
REQUIRED_PACKAGES = ["flask", "flask-cors", "requests"]

# ==================== UTILITIES ====================
def cmd(command, shell=False, check=False):
    """Run a shell command and return stdout or None."""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║   🚀 ULTIMATE AI CHAT WEB – AUTO LAUNCHER  ║
╚══════════════════════════════════════════════╝
""")

def check_python():
    """Ensure Python 3.8+ is installed."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Python 3.8+ is required. Please upgrade.")
        sys.exit(1)
    print(f"✅ Python {sys.version}")

def check_pip():
    """Ensure pip is available. If not, install it."""
    if cmd([sys.executable, "-m", "pip", "--version"]) is None:
        print("📦 pip not found. Installing...")
        # Try to install via ensurepip or apt
        if cmd(["python3", "-m", "ensurepip", "--upgrade"], check=False) is None:
            # Fallback to apt
            if platform.system() == "Linux":
                cmd(["sudo", "apt", "update"], shell=False)
                cmd(["sudo", "apt", "install", "-y", "python3-pip"], shell=False)
            else:
                print("❌ Cannot install pip automatically. Please install pip manually.")
                sys.exit(1)
    print("✅ pip is available")

def install_packages():
    """Install required Python packages if missing."""
    print("📦 Checking Python packages...")
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"   Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ All Python packages are ready.")

def check_server_files():
    """Verify that server.py and index.html exist."""
    if not os.path.exists(SERVER_FILE):
        print(f"❌ {SERVER_FILE} not found in current directory.")
        print(f"   Please place {SERVER_FILE} in the same directory as run.py")
        sys.exit(1)
    if not os.path.exists(INDEX_FILE):
        print(f"❌ {INDEX_FILE} not found. Creating a simple one...")
        create_default_index()
    print("✅ Server files found.")

def create_default_index():
    """Create a minimal index.html if missing."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f0f1a; color: #eaeaea; display: flex; justify-content: center; align-items: center; height: 100vh; margin:0; }
        .container { text-align: center; }
        h1 { color: #e94560; }
        a { color: #e94560; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Chat Web</h1>
        <p>Server is running. <a href="/api/models">View models API</a></p>
    </div>
</body>
</html>"""
    with open(INDEX_FILE, "w") as f:
        f.write(html)

# ==================== SERVER START ====================
def start_server():
    """Start Flask server as a subprocess."""
    print(f"🌐 Starting Flask server on port {PORT}...")
    env = os.environ.copy()
    env["PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, SERVER_FILE],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait briefly to check if it started
    time.sleep(3)
    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"❌ Server failed to start:\n{stderr.decode()}")
        sys.exit(1)
    print(f"✅ Server is running at http://localhost:{PORT}")
    return proc

# ==================== TUNNEL METHODS ====================
def find_executable(name):
    """Check if an executable is available in PATH."""
    return shutil.which(name)

def download_cloudflared():
    """Download cloudflared binary for Linux (amd64)."""
    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    try:
        print("📥 Downloading cloudflared...")
        urllib.request.urlretrieve(url, "cloudflared")
        os.chmod("cloudflared", 0o755)
        # Move to /usr/local/bin if possible, otherwise use current dir
        if os.path.exists("/usr/local/bin") and os.access("/usr/local/bin", os.W_OK):
            shutil.move("cloudflared", "/usr/local/bin/cloudflared")
            return "/usr/local/bin/cloudflared"
        else:
            return os.path.abspath("cloudflared")
    except Exception as e:
        print(f"❌ Failed to download cloudflared: {e}")
        return None

def try_cloudflare_tunnel():
    """Attempt to create a Cloudflare Tunnel."""
    cloudflared_path = find_executable("cloudflared")
    if not cloudflared_path:
        print("⚠️  cloudflared not found. Attempting to download...")
        cloudflared_path = download_cloudflared()
        if not cloudflared_path:
            return None

    print("🔗 Creating Cloudflare Tunnel...")
    try:
        proc = subprocess.Popen(
            [cloudflared_path, "tunnel", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        # Wait for the URL to appear (usually in stderr)
        for _ in range(60):
            line = proc.stderr.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            # Look for the URL pattern
            match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print(f"\n🎉 Public URL: {url}")
                print("   (Cloudflare Tunnel)")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ Cloudflare Tunnel error: {e}")
    return None

def try_localhost_run():
    """Try localhost.run via SSH (no installation needed)."""
    print("⚠️  Trying localhost.run (via SSH)...")
    if not find_executable("ssh"):
        print("❌ SSH client not found. Cannot use localhost.run.")
        return None

    try:
        proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-R", f"80:localhost:{PORT}", "localhost.run"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        # The URL is printed in stdout
        for _ in range(60):
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            print(line, end="")  # Show progress
            if "https://" in line:
                # Extract URL (usually the last line)
                match = re.search(r'https://[a-zA-Z0-9.-]+\.lhr\.life', line)
                if match:
                    url = match.group(0)
                    print(f"\n🎉 Public URL: {url}")
                    print("   (localhost.run)")
                    return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ localhost.run error: {e}")
    return None

def try_ngrok():
    """Try ngrok if installed."""
    ngrok_path = find_executable("ngrok")
    if not ngrok_path:
        return None
    print("⚠️  Trying ngrok...")
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
                print("   (ngrok)")
                return proc, url
        proc.kill()
    except Exception as e:
        print(f"❌ ngrok error: {e}")
    return None

def create_tunnel():
    """Try all methods in order: cloudflared → localhost.run → ngrok."""
    print("\n🔗 Creating public URL...")

    # 1. Cloudflare Tunnel (best, stable)
    result = try_cloudflare_tunnel()
    if result:
        return result

    # 2. localhost.run (no installation, SSH required)
    result = try_localhost_run()
    if result:
        return result

    # 3. ngrok (if installed)
    result = try_ngrok()
    if result:
        return result

    print("\n❌ Could not create tunnel automatically.")
    print(f"   ➡️  Server is running at http://localhost:{PORT}")
    print("   ➡️  To get public URL manually:")
    print("       - Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
    print(f"       - Run: cloudflared tunnel --url http://localhost:{PORT}")
    print("       - Or: ssh -R 80:localhost:5000 localhost.run")
    return None, None

# ==================== CLEANUP & MAIN ====================
def cleanup(server_proc, tunnel_proc):
    """Kill subprocesses on exit."""
    print("\n🛑 Shutting down...")
    if tunnel_proc:
        tunnel_proc.kill()
    if server_proc:
        server_proc.kill()
    print("👋 Goodbye!")

def main():
    print_banner()
    check_python()
    check_pip()
    install_packages()
    check_server_files()

    # Start server
    server_proc = start_server()

    # Create tunnel
    tunnel_proc, url = create_tunnel()

    # Register cleanup
    atexit.register(cleanup, server_proc, tunnel_proc)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

    print(f"\n✨ Server running at http://localhost:{PORT}")
    if url:
        print(f"✨ Public URL: {url}")
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
