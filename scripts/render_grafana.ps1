param(
  [string]$OutDir = $(Join-Path "data\\dashshots" (Get-Date -Format "yyyyMMdd_HHmmss")),
  [string]$From = "now-15m",
  [string]$To = "now",
  [int[]]$Panels = @(),          # auto-discover if empty
  [int]$Width = 1200,
  [int]$Height = 500
)
$ErrorActionPreference = "Stop"
$null = New-Item -ItemType Directory -Force -Path $OutDir

$base = "http://localhost:3000"
$uid  = "toyprod-main"
$slug = "toyprod-service-overview"
$tz   = "UTC"
$kiosk = "tv"

# Auto-discover panel ids from provisioned dashboard json
if ($Panels.Count -eq 0) {
  try {
    $dash = Get-Content -Raw "ops/grafana/provisioning/dashboards/toyprod.json" | ConvertFrom-Json
    $Panels = @($dash.panels | ForEach-Object { $_.id }) | Where-Object { $_ -ne $null }
  } catch { $Panels = @(1,2,3) }
}

# Full dashboard
$dashUrl = "$base/render/d/$uid/$slug?orgId=1&from=$From&to=$To&width=1600&height=1000&tz=$tz&kiosk=$kiosk"
Invoke-WebRequest -UseBasicParsing -Uri $dashUrl -OutFile (Join-Path $OutDir "dashboard.png")

# Each panel via full dashboard route + viewPanel
foreach ($panelId in $Panels) {
  $url = "$base/render/d/$uid/$slug?orgId=1&viewPanel=$panelId&fullscreen=1&from=$From&to=$To&width=$Width&height=$Height&tz=$tz&kiosk=$kiosk"
  Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile (Join-Path $OutDir ("panel-{0}.png" -f $panelId))
}

Write-Host ("Saved to: {0}" -f (Resolve-Path $OutDir).Path)