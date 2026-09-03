#!/usr/bin/env bash
# Claude Code 스킬 5종(agent-browser, find-skills, design-taste-frontend,
# mcp-builder, GSD)과 agent-browser CLI가 이 컴퓨터에 있는지 확인하고,
# 없는 것만 설치한다. 여러 번 실행해도 안전하다(이미 있으면 건너뜀).
#
# 사용법:
#   bash scripts/setup_claude_skills.sh          # 없는 것 설치
#   bash scripts/setup_claude_skills.sh --check  # 확인만 하고 설치하지 않음
#
# 왜 스크립트로 두는가: 프로젝트 스킬(.claude/skills)은 git으로 따라오지만
# GSD와 agent-browser CLI는 컴퓨터마다 따로 설치해야 하므로, 새 환경에서
# 무엇이 빠졌는지 사람이 기억하지 않아도 되게 한다.

set -u

CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MISSING=()
FAILED=()

say()  { printf '  %s\n' "$*"; }
ok()   { printf '  [OK]   %s\n' "$*"; }
miss() { printf '  [없음] %s\n' "${*:2}"; MISSING+=("$1"); }
fail() { printf '  [실패] %s\n' "${*:2}"; FAILED+=("$1"); }

run() {
  # 설치 명령은 --check 모드에서는 출력만 하고 실행하지 않는다.
  if [ "$CHECK_ONLY" = 1 ]; then say "(실행 예정) $*"; return 0; fi
  say "\$ $*"
  "$@"
}

echo "== 1. Node.js =="
if command -v node >/dev/null 2>&1; then
  NODE_VER="$(node --version | sed 's/^v//')"
  NODE_MAJOR="${NODE_VER%%.*}"
  NODE_MINOR="$(echo "$NODE_VER" | cut -d. -f2)"
  if [ "$NODE_MAJOR" -gt 22 ] || { [ "$NODE_MAJOR" -eq 22 ] && [ "$NODE_MINOR" -ge 20 ]; }; then
    ok "node v$NODE_VER (22.20 이상)"
  else
    fail "node" "v$NODE_VER 는 22.20 미만. https://nodejs.org 에서 22 LTS 이상을 먼저 설치하세요."
    echo; echo "Node 버전이 낮아 중단합니다."; exit 1
  fi
else
  fail "node" "node 가 없습니다. https://nodejs.org 에서 22 LTS 이상을 먼저 설치하세요."
  exit 1
fi

echo; echo "== 2. 프로젝트 스킬 (.claude/skills) =="
# 스킬 이름 -> npx skills add 인자. 저장소에 커밋되어 있어 보통은 모두 존재한다.
declare -A SKILL_SRC=(
  [agent-browser]="vercel-labs/agent-browser"
  [find-skills]="vercel-labs/skills --skill find-skills"
  [design-taste-frontend]="https://github.com/Leonxlnx/taste-skill --skill design-taste-frontend"
  [mcp-builder]="anthropics/skills --skill mcp-builder"
)
for name in agent-browser find-skills design-taste-frontend mcp-builder; do
  if [ -f "$REPO_ROOT/.claude/skills/$name/SKILL.md" ]; then
    ok "$name"
  else
    miss "$name" "$name 스킬 없음"
    # shellcheck disable=SC2086
    (cd "$REPO_ROOT" && run npx --yes skills@latest add ${SKILL_SRC[$name]} --agent claude-code --yes --copy) \
      || fail "$name" "$name 설치 실패"
  fi
done

echo; echo "== 3. GSD (전역, $CLAUDE_HOME/skills/gsd-*) =="
if [ -f "$CLAUDE_HOME/skills/gsd-help/SKILL.md" ]; then
  ok "GSD $(cat "$CLAUDE_HOME/gsd-core/VERSION" 2>/dev/null || echo '(버전 파일 없음)')"
else
  miss "gsd" "GSD 없음"
  # GSD 설치기는 ~/.claude/settings.json 에 hooks/statusLine 을 추가한다.
  # 기존 설정을 잃지 않도록 설치 전에 날짜가 붙은 사본을 남긴다.
  if [ -f "$CLAUDE_HOME/settings.json" ] && [ "$CHECK_ONLY" = 0 ]; then
    BK="$CLAUDE_HOME/settings.json.bak-$(date +%Y%m%d-%H%M%S)"
    cp "$CLAUDE_HOME/settings.json" "$BK" && say "settings.json 백업: $BK"
  fi
  run npx --yes @opengsd/gsd-core@latest --claude --global || fail "gsd" "GSD 설치 실패"
fi

echo; echo "== 4. agent-browser CLI (전역 npm) =="
if command -v agent-browser >/dev/null 2>&1; then
  ok "agent-browser $(agent-browser --version 2>/dev/null | awk '{print $2}')"
else
  miss "agent-browser-cli" "agent-browser 명령 없음"
  if run npm install -g agent-browser; then
    # 브라우저 본체(Chrome)도 받아야 실제로 화면을 열 수 있다.
    run agent-browser install || fail "agent-browser-chrome" \
      "Chrome 다운로드 실패. 프록시 환경이면 AGENT_BROWSER_EXECUTABLE_PATH 에 기존 Chromium 경로를 지정하세요."
  else
    fail "agent-browser-cli" "npm install -g agent-browser 실패"
  fi
fi

echo; echo "== 결과 =="
if [ "$CHECK_ONLY" = 1 ]; then
  [ "${#MISSING[@]}" -eq 0 ] && say "모두 설치되어 있습니다." \
    || say "없는 항목 ${#MISSING[@]}개: ${MISSING[*]}  -> 설치하려면 --check 없이 다시 실행"
  exit 0
fi
if [ "${#FAILED[@]}" -eq 0 ]; then
  [ "${#MISSING[@]}" -eq 0 ] && say "모두 이미 설치되어 있어 아무것도 바꾸지 않았습니다." \
    || say "새로 설치: ${MISSING[*]}. GSD 를 새로 설치했다면 Claude Code 를 재시작하세요."
  exit 0
else
  say "실패 항목 ${#FAILED[@]}개: ${FAILED[*]}"
  exit 1
fi
