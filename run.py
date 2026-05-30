#!/usr/bin/env python3
"""
Ultimate AI Chat Web – Auto Setup & Launch
1. Checks & installs dependencies
2. Starts Flask server on port 5000
3. Creates public URL via Cloudflare Tunnel or localhost.run
"""

import os, sys, subprocess, time, platform, signal, atexit

PORT = 5000
SERVER_FILE = "server.py"
REQUIRED_PACKAGES = ["flask", "flask-cors", "requests"]

def cmd(command, shell=False):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
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

def install_packages():
    """Install required packages if missing."""
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
    print("✅ All dependencies installed.")

def start_server():
    """Start Flask server in a subprocess."""
    print(f"🌐 Starting server on port {PORT}...")
    proc = subprocess.Popen(
        [sys.executable, SERVER_FILE],
        env={**os.environ, "PORT": str(PORT)},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    # Give server a moment to start
    time.sleep(2)
    # Check if process is still running
    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"❌ Server failed to start:\n{stderr.decode()}")
        sys.exit(1)
    return proc

def create_tunnel():
    """Try to create a public URL via cloudflared or localhost.run."""
    print("\n🔗 Creating public URL...")
    
    # Method 1: Cloudflare Tunnel (cloudflared)
    cloudflared_path = cmd(["which", "cloudflared"]) or cmd(["where", "cloudflared"], shell=True) if platform.system() == "Windows" else cmd(["which", "cloudflared"])
    
    if cloudflared_path:
        print("✅ Found cloudflared, creating Cloudflare Tunnel...")
        try:
            tunnel_proc = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"http://localhost:{PORT}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # Wait for URL to appear
            for _ in range(30):
                line = tunnel_proc.stderr.readline().decode()
                if "trycloudflare.com" in line:
                    # Extract URL
                    import re
                    match = re.search(r'https://[a-zA-Z0-9.-]+\.trycloudflare\.com', line)
                    if match:
                        print(f"\n🎉 Public URL: {match.group(0)}")
                        print("   (Cloudflare Tunnel)")
                        return tunnel_proc
                if tunnel_proc.poll() is not None:
                    break
                time.sleep(0.5)
            # If not found in stderr, try stdout
            tunnel_proc.kill()
        except FileNotFoundError:
            pass
    
    # Method 2: localhost.run (SSH-based, no installation needed)
    print("⚠️  cloudflared not found. Trying localhost.run...")
    print("   (You need SSH client. Press Ctrl+C to cancel)")
    try:
        tunnel_proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{PORT}", "localhost.run"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # Read output until we get a URL
        for _ in range(60):
            line = tunnel_proc.stdout.readline().decode()
            if "localhost.run" in line or "https://" in line:
                print(f"\n🎉 Public URL: {line.strip()}")
                return tunnel_proc
            if tunnel_proc.poll() is not None:
                break
            time.sleep(0.5)
        tunnel_proc.kill()
    except FileNotFoundError:
        print("❌ SSH not found. Cannot create tunnel.")
    
    # Method 3: ngrok (if installed)
    ngrok_path = cmd(["which", "ngrok"]) or cmd(["where", "ngrok"], shell=True)
    if ngrok_path:
        print("⚠️  Trying ngrok...")
        try:
            tunnel_proc = subprocess.Popen(
                ["ngrok", "http", str(PORT), "--log=stdout"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            for _ in range(30):
                line = tunnel_proc.stdout.readline().decode()
                if "url=" in line:
                    import re
                    match = re.search(r'url=(https://[^\s]+)', line)
                    if match:
                        print(f"\n🎉 Public URL: {match.group(1)}")
                        return tunnel_proc
                if tunnel_proc.poll() is not None:
                    break
                time.sleep(0.5)
            tunnel_proc.kill()
        except FileNotFoundError:
            pass
    
    print("\n❌ Could not create tunnel automatically.")
    print(f"   ➡️  Server is running at http://localhost:{PORT}")
    print("   ➡️  To get public URL manually:")
    print("       - Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
    print(f"       - Run: cloudflared tunnel --url http://localhost:{PORT}")
    print("       - Or use: ssh -R 80:localhost:5000 localhost.run")
    return None

def cleanup(server_proc, tunnel_proc):
    """Clean up processes on exit."""
    print("\n🛑 Shutting down...")
    if tunnel_proc:
        tunnel_proc.kill()
    if server_proc:
        server_proc.kill()
    print("👋 Goodbye!")

def main():
    print_banner()
    check_python()
    install_packages()
    
    if not os.path.exists(SERVER_FILE):
        print(f"❌ {SERVER_FILE} not found in current directory.")
        sys.exit(1)
    if not os.path.exists("index.html"):
        print("❌ index.html not found. Please create it first.")
        sys.exit(1)
    
    server_proc = start_server()
    tunnel_proc = create_tunnel()
    
    # Register cleanup
    atexit.register(cleanup, server_proc, tunnel_proc)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))
    
    print(f"\n✨ Server running at http://localhost:{PORT}")
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
