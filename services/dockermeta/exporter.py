from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import CollectorRegistry, Gauge, CONTENT_TYPE_LATEST, generate_latest
import docker

cli = docker.DockerClient(base_url="unix://var/run/docker.sock")

def build_registry():
    r = CollectorRegistry()
    # NOTE: include full 64-char container_id; keep service and name for convenience
    g = Gauge(
        "docker_container_service_info",
        "Mapping: container -> compose service",
        ["container_id", "service", "name"],
        registry=r
    )
    for c in cli.containers.list(all=True):
        lbls = c.labels or {}
        svc  = lbls.get("com.docker.compose.service", "unknown")
        g.labels(c.id, svc, c.name).set(1)  # c.id is full 64-hex
    return r

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        data = generate_latest(build_registry())
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    HTTPServer(("", 9101), H).serve_forever()
