import time, docker
from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST

cli = docker.from_env()

def get_docker_stats():
    registry = CollectorRegistry()

    cpu_usage = Gauge(
        "docker_container_cpu_usage_percent",
        "CPU usage percentage per container",
        ["container_id", "name"],
        registry=registry
    )
    mem_usage = Gauge(
        "docker_container_memory_usage_bytes",
        "Memory usage in bytes per container",
        ["container_id", "name"],
        registry=registry
    )
    mem_limit = Gauge(
        "docker_container_memory_limit_bytes",
        "Memory limit in bytes per container",
        ["container_id", "name"],
        registry=registry
    )

    for c in cli.containers.list():
        try:
            stats = c.stats(stream=False)
            if not stats:
                continue

            # Memory Stats
            mem_stats = stats.get("memory_stats", {})
            usage = mem_stats.get("usage")
            limit = mem_stats.get("limit")
            if usage is not None and limit is not None:
                mem_usage.labels(c.id, c.name).set(usage)
                mem_limit.labels(c.id, c.name).set(limit)

            # More robust CPU Stats Calculation
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            if precpu_stats and cpu_stats:
                cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
                system_cpu_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get("system_cpu_usage", 0)
                number_cpus = cpu_stats.get("online_cpus", 1)

                if system_cpu_delta > 0.0 and cpu_delta > 0.0 and number_cpus > 0:
                    percent = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
                    cpu_usage.labels(c.id, c.name).set(percent)

        except Exception:
            continue

    return generate_latest(registry)

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            data = get_docker_stats()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    HTTPServer(("", 9102), H).serve_forever()