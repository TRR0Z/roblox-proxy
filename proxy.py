from mitmproxy import proxy, options, http
from mitmproxy.tools.dump import DumpMaster
from roblox import create_game, upload_game, create_gameserver
from flask import Flask, request
from threading import Thread, Event
from queue import Queue, Empty
from mitmproxy.flow import Error
import rockblox
import requests
import secrets
import sys
import time

request_cache = dict()
request_queue = Queue()
app = Flask("x")

session = rockblox.Session(sys.argv[1], user_agent="Roblox/WinInet")

public_ip = requests.get("https://api.ipify.org?format=json").json()["ip"]
api_port = 80
proxy_port = 3337


def cst():
    while 1:
        try:
            pid = create_game(session, "asdasd")
            with open("game.rbxlx", "r") as f:
                pid = upload_game(session, pid, f.read().replace(
                    "{base_url}", f"http://{public_ip}:{api_port}"
                ))
            joindata = create_gameserver(session, pid)
            print("creating new server ..")
            time.sleep(15)
        except Exception as err:
            print(err)

def sanitize_headers(headers):
    to_remove = ["Host", "Proxy-Connection", "Connection", "sec-fetch-", "User-Agent", "Accept-Encoding", "Content-Length"]
    for kn in to_remove:
        kn = kn.lower()
        for kn2 in list(headers.keys()):
            if kn2.lower().startswith(kn):
                del headers[kn2]
    return headers

class Request:
    def __init__(self, method, url, headers=None, body=None):
        self.id = secrets.token_hex(4)
        self.method = method
        self.url = url
        self.headers = sanitize_headers(headers)
        self.body = body
        self.response = None
        self.event = Event()
    
    def complete(self, response=None):
        if response:
            if "content-encoding" in response["headers"]:
                del response["headers"]["content-encoding"]
            response["headers"]["content-length"] = str(len(response["body"]))
            self.response = response
        self.event.set()
    
    def to_dict(self):
        return {
            "id": self.id,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body
        }

def submit_request(request: Request):
    try:
        request_cache[request.id] = request
        request_queue.put(request)
        request.event.wait(30)
    finally:
        del request_cache[request.id]
    return request.response

@app.route("/get-request")
def get_request_route():
    try:
        req = request_queue.get(False)
        return req.to_dict()
    except:
        return "Not Found", 404

@app.route("/complete-request", methods=["POST"])
def complete_request_route():
    data = request.get_json()
    req = request_cache[data["id"]]
    req.complete(data.get("response"))
    return "OK", 200

class Addon:
    def request(self, flow: http.HTTPFlow):
        if "mitm.it" in flow.request.url:
            return
        
        data = flow.request.data.content.decode("UTF-8")
        if not len(data):
            data = None
        req = Request(flow.request.method, flow.request.url,
                      dict(flow.request.headers), data)
        resp = submit_request(req)
        
        if resp:
            flow.response = http.HTTPResponse.make(
                resp["status"],
                resp["body"].encode("UTF-8"),
                resp["headers"]
            )

        else:
            flow.error = Error("Gameserver did not send response")
            flow.response = http.HTTPResponse.make(
                400, b"The gameserver returned no response for this request.", {})

## start flask
Thread(target=app.run, kwargs=dict(host="0.0.0.0", port=api_port)).start()
Thread(target=cst).start()

## start mitmproxy
opts = options.Options(listen_host="127.0.0.1", listen_port=proxy_port)
opts.add_option("body_size_limit", int, 0, "")
pconf = proxy.config.ProxyConfig(opts)

m = DumpMaster(None)
m.server = proxy.server.ProxyServer(pconf)
m.addons.add(Addon())
m.run()
