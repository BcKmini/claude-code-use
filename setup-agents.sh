#!/usr/bin/env bash
# Claude Code Multi-Agent System — Mac/Linux 설치 스크립트
# 실행: bash setup-agents.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

echo -e "${CYAN}Claude Code 멀티 에이전트 시스템 세팅 시작...${NC}"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. 글로벌 에이전트 폴더
GLOBAL_AGENT_DIR="$HOME/.claude/agents"
if [ ! -d "$GLOBAL_AGENT_DIR" ]; then
  mkdir -p "$GLOBAL_AGENT_DIR"
  echo -e "${GREEN}글로벌 에이전트 폴더 생성됨: $GLOBAL_AGENT_DIR${NC}"
else
  echo -e "${GREEN}글로벌 에이전트 폴더 확인됨: $GLOBAL_AGENT_DIR${NC}"
fi

# 2. 에이전트 파일 복사
AGENT_SRC="$SCRIPT_DIR/agents"
if [ -d "$AGENT_SRC" ]; then
  cp "$AGENT_SRC"/*.md "$GLOBAL_AGENT_DIR/"
  COUNT=$(ls "$AGENT_SRC"/*.md 2>/dev/null | wc -l | tr -d ' ')
  echo -e "${GREEN}에이전트 파일 ${COUNT}개 복사 완료 -> $GLOBAL_AGENT_DIR${NC}"
else
  echo -e "${YELLOW}경고: agents/ 폴더를 찾을 수 없습니다. 수동으로 복사해주세요.${NC}"
fi

# 3. Agent Teams 환경변수 설정
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$(basename "$SHELL")" = "bash" ]; then
  SHELL_RC="$HOME/.bashrc"
  # macOS 기본 셸은 .bash_profile 사용
  if [[ "$OSTYPE" == "darwin"* ]] && [ -f "$HOME/.bash_profile" ]; then
    SHELL_RC="$HOME/.bash_profile"
  fi
fi

ENV_LINE='export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1'
if [ -n "$SHELL_RC" ]; then
  if grep -qF "$ENV_LINE" "$SHELL_RC" 2>/dev/null; then
    echo -e "${GREEN}Agent Teams 환경변수 이미 설정됨 ($SHELL_RC)${NC}"
  else
    echo "" >> "$SHELL_RC"
    echo "# Claude Code Agent Teams" >> "$SHELL_RC"
    echo "$ENV_LINE" >> "$SHELL_RC"
    echo -e "${GREEN}Agent Teams 환경변수 추가됨 -> $SHELL_RC${NC}"
  fi
else
  echo -e "${YELLOW}셸 설정 파일을 감지하지 못했습니다. 수동으로 추가해주세요:${NC}"
  echo -e "  ${GRAY}$ENV_LINE${NC}"
fi

# 현재 세션에도 즉시 적용
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# 4. .claudeignore 생성 (토큰 절약)
if [ ! -f ".claudeignore" ]; then
  cat > .claudeignore << 'EOF'
node_modules/
dist/
build/
.git/
*.lock
coverage/
.next/
*.log
*.map
EOF
  echo -e "${GREEN}.claudeignore 생성됨${NC}"
fi

# 5. 완료
echo
echo -e "${CYAN}세팅 완료!${NC}"
echo
echo -e "${YELLOW}다음 단계:${NC}"
echo -e "  1. 셸 재시작 또는 아래 명령 실행:"
if [ -n "$SHELL_RC" ]; then
  echo -e "     ${GRAY}source $SHELL_RC${NC}"
fi
echo -e "  2. claude 실행 후 /agents 명령으로 확인"
echo -e "  3. CLAUDE.md를 프로젝트에 맞게 수정"
echo
echo -e "${YELLOW}사용 예시:${NC}"
echo -e "  ${GRAY}> Use the orchestrator to add OAuth login${NC}"
echo -e "  ${GRAY}> Have reviewer check src/auth/login.ts${NC}"
echo -e "  ${GRAY}> Have harness-designer design a pipeline for [task]${NC}"
echo -e "  ${GRAY}> /pipeline run analyze and patch slow queries${NC}"
echo
echo -e "${YELLOW}도구 설치 (선택):${NC}"
echo -e "  ${GRAY}make install-tools   # Python 도구 설치 (harness, pipeline 포함)${NC}"
