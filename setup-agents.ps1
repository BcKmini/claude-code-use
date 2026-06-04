# Claude Code 멀티 에이전트 세팅 스크립트 (Windows PowerShell)
# 실행: powershell -ExecutionPolicy Bypass -File setup-agents.ps1

Write-Host "🤖 Claude Code 멀티 에이전트 시스템 세팅 시작..." -ForegroundColor Cyan

# 1. 글로벌 에이전트 폴더 (모든 프로젝트에서 사용)
$globalAgentDir = "$env:USERPROFILE\.claude\agents"
if (-not (Test-Path $globalAgentDir)) {
    New-Item -ItemType Directory -Path $globalAgentDir -Force | Out-Null
    Write-Host "✅ 글로벌 에이전트 폴더 생성됨: $globalAgentDir" -ForegroundColor Green
}

# 2. 에이전트 파일 복사
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentsSource = Join-Path $scriptDir "agents"
if (Test-Path $agentsSource) {
    Copy-Item "$agentsSource\*.md" $globalAgentDir -Force
    Write-Host "✅ 에이전트 파일 복사 완료 ($globalAgentDir)" -ForegroundColor Green
} else {
    Write-Host "⚠️  agents/ 폴더를 찾을 수 없습니다. 수동으로 복사해주세요." -ForegroundColor Yellow
}

# 3. Agent Teams 활성화 (현재 세션)
$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"

# 영구 적용 (사용자 환경변수)
[System.Environment]::SetEnvironmentVariable(
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", 
    "1", 
    "User"
)
Write-Host "✅ Agent Teams 활성화됨" -ForegroundColor Green

# 4. .claudeignore 생성 (토큰 절약)
$claudeignore = @"
node_modules/
dist/
build/
.git/
*.lock
coverage/
.next/
*.log
*.map
"@
if (-not (Test-Path ".claudeignore")) {
    $claudeignore | Out-File -FilePath ".claudeignore" -Encoding UTF8
    Write-Host "✅ .claudeignore 생성됨" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 세팅 완료!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 다음 단계:" -ForegroundColor Yellow
Write-Host "  1. claude 실행 후 /agents 명령으로 확인" -ForegroundColor White
Write-Host "  2. CLAUDE.md를 프로젝트에 맞게 수정" -ForegroundColor White
Write-Host ""
Write-Host "💡 사용 예시:" -ForegroundColor Yellow
Write-Host "  > Use the orchestrator to add OAuth login" -ForegroundColor Gray
Write-Host "  > Have reviewer check src/auth/login.ts" -ForegroundColor Gray
