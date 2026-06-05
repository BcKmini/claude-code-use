# install-snippet.ps1
# snippet 도구를 현재 Windows 환경에 설치한다.
#
# 실행 방법:
#   powershell -ExecutionPolicy Bypass -File tools\install-snippet.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "=== snippet 설치 ===" -ForegroundColor Cyan
Write-Host ""

# ── 1. Python 확인 ────────────────────────────────────────────────────────────
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") {
            $python = $cmd
            break
        }
    } catch { }
}

if (-not $python) {
    Write-Host "[ERROR] Python 3가 필요합니다." -ForegroundColor Red
    Write-Host "  설치: winget install Python.Python.3"
    exit 1
}
Write-Host "[OK] Python 확인됨: $python" -ForegroundColor Green

# ── 2. .claude/commands/ 디렉터리 생성 ────────────────────────────────────────
$CommandsDir = Join-Path $HOME ".claude\commands"
if (-not (Test-Path $CommandsDir)) {
    New-Item -ItemType Directory -Force -Path $CommandsDir | Out-Null
    Write-Host "[OK] 생성됨: $CommandsDir" -ForegroundColor Green
} else {
    Write-Host "[OK] 존재함: $CommandsDir" -ForegroundColor Green
}

# ── 3. /snippet 슬래시 커맨드 설치 ───────────────────────────────────────────
$Src = Join-Path $RepoRoot ".claude\commands\snippet.md"
$Dst = Join-Path $CommandsDir "snippet.md"
Copy-Item -Force $Src $Dst
Write-Host "[OK] 슬래시 커맨드 설치됨: $Dst" -ForegroundColor Green

# ── 4. 기본 스니펫 임포트 ────────────────────────────────────────────────────
$DefaultsFile = Join-Path $RepoRoot "snippets\defaults.json"
Write-Host ""
Write-Host "기본 스니펫(13개)을 가져오겠습니까? [Y/n] " -NoNewline
$answer = Read-Host
if ($answer -eq "" -or $answer -match "^[Yy]") {
    & $python (Join-Path $RepoRoot "tools\snippet.py") import $DefaultsFile
    Write-Host "[OK] 기본 스니펫 임포트 완료" -ForegroundColor Green
}

# ── 5. snippet 단축 명령 등록 (PowerShell 프로파일) ──────────────────────────
$ProfilePath = $PROFILE
if (-not (Test-Path $ProfilePath)) {
    New-Item -ItemType File -Force -Path $ProfilePath | Out-Null
}

$FuncDef = @"

# snippet — Claude Code 프롬프트 매니저
function snippet {
    python "$($RepoRoot.Replace('\','\\'))\\tools\\snippet.py" @args
}
"@

$ProfileContent = Get-Content $ProfilePath -Raw -ErrorAction SilentlyContinue
if ($ProfileContent -notmatch "Claude Code 프롬프트 매니저") {
    Add-Content -Path $ProfilePath -Value $FuncDef
    Write-Host "[OK] PowerShell 프로파일에 'snippet' 함수 등록됨" -ForegroundColor Green
    Write-Host "     적용: . `$PROFILE" -ForegroundColor DarkGray
} else {
    Write-Host "[OK] 'snippet' 함수 이미 등록되어 있음" -ForegroundColor Green
}

# ── 완료 ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "설치 완료!" -ForegroundColor Cyan
Write-Host ""
Write-Host "사용 방법:"
Write-Host "  터미널  : snippet list"
Write-Host "  터미널  : snippet run full-pipeline"
Write-Host "  Claude  : /snippet list"
Write-Host "  Claude  : /snippet run full-pipeline"
Write-Host ""
Write-Host "새 터미널을 열거나 '. `$PROFILE' 을 실행하면 'snippet' 명령이 활성화됩니다."
Write-Host ""
