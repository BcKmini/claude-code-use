# install-tools.ps1
# Installs all three Claude Code productivity tools:
#   snippet      -- personal prompt manager
#   claude-handoff -- session continuity
#   claude-cost  -- cost predictor & tracker
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File tools\install-tools.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Claude Code Tools Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Python check ───────────────────────────────────────────────────────────
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") { $python = $cmd; break }
    } catch { }
}
if (-not $python) {
    Write-Host "[ERROR] Python 3 is required." -ForegroundColor Red
    Write-Host "  Install: winget install Python.Python.3"
    exit 1
}
Write-Host "[OK] Python: $python" -ForegroundColor Green

# ── 2. ~/.claude/commands/ ────────────────────────────────────────────────────
$CommandsDir = Join-Path $HOME ".claude\commands"
if (-not (Test-Path $CommandsDir)) {
    New-Item -ItemType Directory -Force -Path $CommandsDir | Out-Null
}
foreach ($cmd in @("snippet.md", "handoff.md", "cost.md")) {
    $src = Join-Path $RepoRoot ".claude\commands\$cmd"
    $dst = Join-Path $CommandsDir $cmd
    Copy-Item -Force $src $dst
}
Write-Host "[OK] Slash commands installed: /snippet  /handoff  /cost" -ForegroundColor Green

# ── 3. Import default snippets ────────────────────────────────────────────────
$DefaultsFile = Join-Path $RepoRoot "snippets\defaults.json"
& $python (Join-Path $RepoRoot "tools\snippet.py") import $DefaultsFile 2>&1 | Out-Null
Write-Host "[OK] Default snippets imported (20)" -ForegroundColor Green

# ── 4. Register shell functions in PowerShell profile ────────────────────────
$ProfilePath = $PROFILE
if (-not (Test-Path $ProfilePath)) {
    New-Item -ItemType File -Force -Path $ProfilePath | Out-Null
}

$FuncDef = @"

# ── Claude Code Tools ──────────────────────────────────────────────────────
function snippet       { python "$($RepoRoot.Replace('\','\\'))\\tools\\snippet.py" @args }
function claude-handoff { python "$($RepoRoot.Replace('\','\\'))\\tools\\claude-handoff.py" @args }
function claude-cost   { python "$($RepoRoot.Replace('\','\\'))\\tools\\claude-cost.py" @args }
# ──────────────────────────────────────────────────────────────────────────
"@

$existing = Get-Content $ProfilePath -Raw -ErrorAction SilentlyContinue
if ($existing -notmatch "Claude Code Tools") {
    Add-Content -Path $ProfilePath -Value $FuncDef
    Write-Host "[OK] Shell functions registered in PowerShell profile" -ForegroundColor Green
    Write-Host "     Apply now: . `$PROFILE" -ForegroundColor DarkGray
} else {
    Write-Host "[OK] Shell functions already registered" -ForegroundColor Green
}

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installation complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal commands:"
Write-Host "  snippet list"
Write-Host "  claude-handoff save"
Write-Host "  claude-handoff load | claude"
Write-Host "  claude-cost estimate --snippet full-pipeline"
Write-Host ""
Write-Host "Inside Claude Code:"
Write-Host "  /snippet list"
Write-Host "  /handoff save"
Write-Host "  /cost estimate full-pipeline"
Write-Host ""
Write-Host "Open a new terminal or run '. `$PROFILE' to activate." -ForegroundColor Yellow
Write-Host ""
