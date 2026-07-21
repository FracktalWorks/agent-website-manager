# Auto-discovers the Open Design daemon port and launches the MCP server.
# The daemon uses dynamic ports, so this script finds it every time.
$ErrorActionPreference = "SilentlyContinue"

# Find the daemon port by checking all node processes' listening ports
$nodePids = Get-Process node -ErrorAction SilentlyContinue | ForEach-Object { $_.Id }
$daemonPort = $null

foreach ($procId in $nodePids) {
    $lines = & netstat -ano 2>$null | Select-String "$procId`$" | Select-String "LISTENING" | Select-String "127.0.0.1"
    foreach ($line in $lines) {
        if ($line -match '127\.0\.0\.1:(\d+)') {
            $port = $matches[1]
            # Test if it's the OD daemon by hitting the API
            try {
                $null = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/projects" -TimeoutSec 2
                $daemonPort = $port
                break
            } catch {}
        }
    }
    if ($daemonPort) { break }
}

if (-not $daemonPort) {
    Write-Error "Open Design daemon not found. Start Open Design first."
    exit 1
}

$env:OD_DATA_DIR = "C:\Users\VijayRaghavVarada\Documents\Github\open-design\.od"
& "C:\Program Files\nodejs\node.exe" "C:\Users\VijayRaghavVarada\Documents\Github\open-design\apps\daemon\dist\cli.js" mcp --daemon-url "http://127.0.0.1:$daemonPort"
