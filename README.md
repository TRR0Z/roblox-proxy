# roblox-proxy
Creates a proxy server, utilizing HttpService to mask requests behind Roblox gameserver IPs.

This version is lazily thrown together for demo. purposes, expect a more efficient rewrite.

Windows only, for now.

# Setup
```bash
pip install -U git+https://github.com/h0nde/rockblox.git
pip install mitmproxy
pip install flask
pip install requests
pip install bs4
```

# Usage
Port forward TCP :80

```bash
python3 proxy.py "yourrobloxcookie"
```

```bash
curl --proxy http://localhost:3337 -k http://ip-api.com/json
```
