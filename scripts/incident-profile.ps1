param(
  [int]$qps = 4,
  [switch]$Snapshots
)

function Set-Chaos($delayMs, $failRate) {
  try {
    Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://localhost:8000/chaos?delay_ms=$delayMs&fail_rate=$failRate" | Out-Null
  } catch {}
}

function Invoke-Load($sec, $qps) {
  $intervalMs = [int](1000 / [Math]::Max($qps,1))
  $deadline = (Get-Date).AddSeconds($sec)
  $count = 0
  while ((Get-Date) -lt $deadline) {
    try {
      Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:8000/orders?count=3" | Out-Null
    } catch {}
    Start-Sleep -Milliseconds $intervalMs
    $count++
  }
  return $count
}

$stamp   = Get-Date -Format "yyyyMMdd_HHmmss"
$rootDir = Join-Path "data\incidents" $stamp
$null = New-Item -ItemType Directory -Force -Path $rootDir

$timeline = @()
$started  = (Get-Date).ToUniversalTime().ToString("o")

Write-Host "Warmup: delay=0ms, error rate=0"
Set-Chaos 0 0
$c1 = Invoke-Load 60 $qps
$timeline += @{
  phase="warmup"; delay_ms=0; fail_rate=0; duration_sec=60; requests=$c1;
  endedAt=(Get-Date).ToUniversalTime().ToString("o")
}

Write-Host "Degrade: delay=200ms, error rate=0.2"
Set-Chaos 200 0.2
$c2 = Invoke-Load 90 $qps
$timeline += @{
  phase="degrade"; delay_ms=200; fail_rate=0.2; duration_sec=90; requests=$c2;
  endedAt=(Get-Date).ToUniversalTime().ToString("o")
}

Write-Host "Incident: delay=400ms, error rate=0.5"
Set-Chaos 400 0.5
$c3 = Invoke-Load 120 $qps
$timeline += @{
  phase="incident"; delay_ms=400; fail_rate=0.5; duration_sec=120; requests=$c3;
  endedAt=(Get-Date).ToUniversalTime().ToString("o")
}

Write-Host "Recover: delay=0ms, error rate=0"
Set-Chaos 0 0
$c4 = Invoke-Load 60 $qps
$timeline += @{
  phase="recover"; delay_ms=0; fail_rate=0; duration_sec=60; requests=$c4;
  endedAt=(Get-Date).ToUniversalTime().ToString("o")
}

$ended = (Get-Date).ToUniversalTime().ToString("o")
$incident = [ordered]@{
  startedAt = $started
  endedAt   = $ended
  qps       = $qps
  timeline  = $timeline
}

$incidentPath = Join-Path $rootDir "incident.json"
$incident | ConvertTo-Json -Depth 6 | Out-File -FilePath $incidentPath -Encoding utf8

if ($Snapshots.IsPresent) {
  & powershell -ExecutionPolicy Bypass -NoProfile -File ".\scripts\render_grafana.ps1" -OutDir $rootDir -From "now-15m" -To "now" | Out-Null
}

Write-Host "Incident captured."
Write-Host "  JSON: $incidentPath"
Write-Host "  Folder: $rootDir"
