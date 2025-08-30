param(
  [int]$qps = 4,
  [switch]$Snapshots   # if set, will call render_grafana.ps1 at the end
)

function Set-Chaos($delayMs, $failRate) {
  try { Invoke-WebRequest -UseBasicParsing "http://localhost:8000/chaos?delay_ms=$delayMs&fail_rate=$failRate" | Out-Null } catch {}
}

function Invoke-Load($sec, $qps) {
  $intervalMs = [int](1000 / $qps)
  $deadline = (Get-Date).AddSeconds($sec)
  $count = 0
  while ((Get-Date) -lt $deadline) {
    try { Invoke-WebRequest -UseBasicParsing "http://localhost:8000/orders?count=3" | Out-Null } catch {}
    Start-Sleep -Milliseconds $intervalMs
    $count++
  }
  return $count
}

$stamp   = Get-Date -Format "yyyyMMdd_HHmmss"
$rootDir = Join-Path "data\\incidents" $stamp
$null = New-Item -ItemType Directory -Force -Path $rootDir

$timeline = @()
$started  = (Get-Date).ToUniversalTime().ToString("o")

# Warmup
Write-Host "🔶 Warmup (0% errors, 0ms)"; Set-Chaos 0 0
$c1 = Invoke-Load 60 $qps
$timeline += @{ phase="warmup"; delay_ms=0; fail_rate=0; duration_sec=60; requests=$c1; endedAt=(Get-Date).ToUniversalTime().ToString("o") }

# Degrade
Write-Host "🟠 Degrade (200ms, 20% errors)"; Set-Chaos 200 0.2
$c2 = Invoke-Load 90 $qps
$timeline += @{ phase="degrade"; delay_ms=200; fail_rate=0.2; duration_sec=90; requests=$c2; endedAt=(Get-Date).ToUniversalTime().ToString("o") }

# Incident
Write-Host "🔴 Incident (400ms, 50% errors)"; Set-Chaos 400 0.5
$c3 = Invoke-Load 120 $qps
$timeline += @{ phase="incident"; delay_ms=400; fail_rate=0.5; duration_sec=120; requests=$c3; endedAt=(Get-Date).ToUniversalTime().ToString("o") }

# Recover
Write-Host "🟢 Recover (0ms, 0% errors)"; Set-Chaos 0 0
$c4 = Invoke-Load 60 $qps
$timeline += @{ phase="recover"; delay_ms=0; fail_rate=0; duration_sec=60; requests=$c4; endedAt=(Get-Date).ToUniversalTime().ToString("o") }

$ended = (Get-Date).ToUniversalTime().ToString("o")
$incident = [ordered]@{
  startedAt = $started
  endedAt   = $ended
  qps       = $qps
  timeline  = $timeline
}

$incidentPath = Join-Path $rootDir "incident.json"
$incident | ConvertTo-Json -Depth 6 | Out-File -FilePath $incidentPath -Encoding utf8

# Optional: take PNG snapshots covering last 15 minutes (includes the whole run)
if ($Snapshots.IsPresent) {
  & powershell -ExecutionPolicy Bypass -NoProfile -File ".\scripts\render_grafana.ps1" -OutDir $rootDir -From "now-15m" -To "now" | Out-Null
}

Write-Host "✅ Incident captured:"
Write-Host "  JSON: $incidentPath"
Write-Host "  PNGs: $rootDir (if -Snapshots was used)"