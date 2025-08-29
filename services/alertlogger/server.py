from http.server import HTTPServer, BaseHTTPRequestHandler
import json, sys
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n) if n>0 else b""
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {"raw": raw.decode("utf-8", "ignore")}
        sys.stdout.write("ALERTLOGGER " + json.dumps({"path": self.path, "payload": payload}) + "\n")
        sys.stdout.flush()
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"alertlogger running")
HTTPServer(("", 9000), H).serve_forever()