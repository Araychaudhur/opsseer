param(
  [ValidateSet("up","down","ps","logs")]
  [string]$cmd = "up"
)

switch ($cmd) {
  "up"   { docker compose up -d; break }
  "down" { docker compose down -v; break }
  "ps"   { docker compose ps; break }
  "logs" { docker compose logs -f; break }
}
