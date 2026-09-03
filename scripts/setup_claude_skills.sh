#!/usr/bin/env bash
# Claude Code 작업 도구가 이 컴퓨터에 있는지 확인하고, 없는 것만 설치한다.
# 여러 번 실행해도 안전하다(이미 있으면 건너뜀). macOS 기본 bash 3.2에서도 돌도록
# 연관 배열 등 bash 4 전용 문법은 쓰지 않는다.
#
# 사용법:
#   bash scripts/setup_claude_skills.sh            # 없는 것 설치
#   bash scripts/setup_claude_skills.sh --check    # 확인만 하고 설치하지 않음
#   bash scripts/setup_claude_skills.sh --doctor   # 설치 확인 + Headroom 프록시 자가진단까지
#
# 다루는 항목 (세트별)
#   1세트  프로젝트 스킬 4종(.claude/skills, git으로 따라옴), GSD, agent-browser CLI
#   2세트  Context7(ctx7), Strix, Graphify, Headroom, Ponytail, ECC
#   3세트  MCP 서버 5종(playwright, chrome-devtools, glif, perplexity, firecrawl)
#
# 중복 설치를 막는 규칙 (조사로 확인한 사실에 근거)
#   - Ponytail: 계정 동기화 스킬(~/.claude/skills/synced/*/ponytail)이 이미 있으면
#     플러그인을 설치하지 않는다. 같은 스킬이 두 벌 생기기 때문이다.
#   - Graphify: GSD의 gsd-graphify 는 외부 graphify CLI(PyPI: graphifyy)를 "요구"한다.
#     중복이 아니라 의존성이므로 설치한다. 단 CLI와 스킬을 각각 따로 검사한다.
#   - ECC: 터미널에서 자동 설치하지 않는다. 없으면 사용자가 대화창에 입력할 두 줄을 안내한다.
#   - API 키가 필요한 MCP(perplexity, firecrawl)는 환경 변수에 키가 있을 때만 등록하고,
#     키 값은 절대 화면에 찍지 않는다.

set -u

MODE=install
case "${1:-}" in
  --check)  MODE=check ;;
  --doctor) MODE=doctor ;;
esac
CHECK_ONLY=0; [ "$MODE" = check ] && CHECK_ONLY=1

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MISSING=""; FAILED=""; NOTES=""

say()  { printf '  %s\n' "$*"; }
ok()   { printf '  [OK]   %s\n' "$*"; }
miss() { printf '  [없음] %s\n' "${*:2}"; MISSING="$MISSING $1"; }
fail() { printf '  [실패] %s\n' "${*:2}"; FAILED="$FAILED $1"; }
note() { printf '  [안내] %s\n' "$*"; NOTES="$NOTES
  - $*"; }

run() {
  # 설치 명령은 --check 모드에서는 출력만 하고 실행하지 않는다.
  if [ "$CHECK_ONLY" = 1 ]; then say "(실행 예정) $*"; return 0; fi
  say "\$ $*"
  "$@"
}

backup_file() {
  # 설치기가 건드리는 설정 파일은 날짜 붙은 사본을 먼저 남긴다(덮어쓰기 방지).
  [ -f "$1" ] || return 0
  [ "$CHECK_ONLY" = 1 ] && return 0
  local bk="$1.bak-$(date +%Y%m%d-%H%M%S)"
  cp "$1" "$bk" && say "백업: $bk"
}

version_ge() {
  # version_ge 22.22.2 22.20  → 앞이 뒤 이상이면 0
  [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

# ──────────────────────────────────────────────────────────────
echo "== 1. 기본 도구 (node / claude / uv / docker) =="
if command -v node >/dev/null 2>&1; then
  NODE_VER="$(node --version | sed 's/^v//')"
  if version_ge "$NODE_VER" 22.20; then ok "node v$NODE_VER (22.20 이상)"
  else fail node "node v$NODE_VER 는 22.20 미만. https://nodejs.org 에서 22 LTS 이상을 먼저 설치하세요."; exit 1; fi
else
  fail node "node 가 없습니다. https://nodejs.org 에서 22 LTS 이상을 먼저 설치하세요."; exit 1
fi

if command -v claude >/dev/null 2>&1; then ok "claude $(claude --version 2>/dev/null | head -1)"
else fail claude "claude 명령이 없습니다. Claude Code 를 먼저 설치하세요: https://docs.claude.com/ko/docs/claude-code/setup"; exit 1; fi

if command -v uv >/dev/null 2>&1; then ok "uv $(uv --version 2>/dev/null | awk '{print $2}')"
else
  miss uv "uv 없음 (Graphify/Headroom 설치에 필요)"
  # 공식 설치 스크립트. PATH 등록을 위해 셸 rc 파일에 한 줄을 추가할 수 있다.
  run sh -c 'curl -LsSf https://astral.sh/uv/install.sh | sh' || fail uv "uv 설치 실패"
  export PATH="$HOME/.local/bin:$PATH"
fi

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then ok "docker 데몬 응답함"
else note "Docker 데몬이 응답하지 않음 → Strix 는 설치는 되지만 실제 스캔은 Docker 가 켜져야 동작"; fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 2. 프로젝트 스킬 (.claude/skills, git 으로 따라옴) =="
for name in agent-browser find-skills design-taste-frontend mcp-builder; do
  if [ -f "$REPO_ROOT/.claude/skills/$name/SKILL.md" ]; then ok "$name"; continue; fi
  miss "$name" "$name 스킬 없음"
  case "$name" in
    agent-browser)         src="vercel-labs/agent-browser" ;;
    find-skills)           src="vercel-labs/skills --skill find-skills" ;;
    design-taste-frontend) src="https://github.com/Leonxlnx/taste-skill --skill design-taste-frontend" ;;
    mcp-builder)           src="anthropics/skills --skill mcp-builder" ;;
  esac
  # shellcheck disable=SC2086
  (cd "$REPO_ROOT" && run npx --yes skills@latest add $src --agent claude-code --yes --copy) || fail "$name" "$name 설치 실패"
done

# ──────────────────────────────────────────────────────────────
echo; echo "== 3. GSD (전역, $CLAUDE_HOME/skills/gsd-*) =="
if [ -f "$CLAUDE_HOME/skills/gsd-help/SKILL.md" ]; then
  ok "GSD $(cat "$CLAUDE_HOME/gsd-core/VERSION" 2>/dev/null || echo '(버전 파일 없음)')"
else
  miss gsd "GSD 없음"
  backup_file "$CLAUDE_HOME/settings.json"   # GSD 설치기는 hooks/statusLine 을 추가한다
  run npx --yes @opengsd/gsd-core@latest --claude --global || fail gsd "GSD 설치 실패"
  note "GSD 를 새로 설치했으면 Claude Code 재시작 필요"
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 4. agent-browser CLI (전역 npm) =="
if command -v agent-browser >/dev/null 2>&1; then
  ok "agent-browser $(agent-browser --version 2>/dev/null | awk '{print $2}')"
else
  miss agent-browser-cli "agent-browser 명령 없음"
  if run npm install -g agent-browser; then
    run agent-browser install || fail agent-browser-chrome \
      "Chrome 다운로드 실패. 프록시 환경이면 AGENT_BROWSER_EXECUTABLE_PATH 에 기존 Chromium 경로를 지정하세요."
  else fail agent-browser-cli "npm install -g agent-browser 실패"; fi
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 5. Context7 (ctx7 → 최신 라이브러리 문서) =="
# ctx7 setup --claude 는 기본적으로 브라우저 로그인을 요구한다(-y 로도 생략 안 됨).
# 자동화에서는 공식 옵션 중 --api-key(키가 환경 변수 CONTEXT7_API_KEY 에 있을 때) 또는
# --oauth(키 없이 MCP 서버만 등록, 이후 Claude Code 의 /mcp 에서 로그인)를 쓴다.
ctx7_present() { claude mcp get context7 >/dev/null 2>&1 || [ -f "$CLAUDE_HOME/skills/context7-mcp/SKILL.md" ] || [ -f "$CLAUDE_HOME/skills/find-docs/SKILL.md" ]; }
if ctx7_present; then
  ok "Context7 설정됨 ($(claude mcp get context7 2>/dev/null | grep -E '^\s*URL:' | awk '{print $2}'))"
else
  miss context7 "Context7 미설정"
  if [ -n "${CONTEXT7_API_KEY:-}" ]; then
    if [ "$CHECK_ONLY" = 1 ]; then say "(실행 예정) npx --yes ctx7@latest setup --claude --mcp --api-key <redacted>"
    else say "\$ npx --yes ctx7@latest setup --claude --mcp --api-key <redacted>"; npx --yes ctx7@latest setup --claude --mcp --api-key "$CONTEXT7_API_KEY" 2>&1 | sed -E 's/ctx7sk-[A-Za-z0-9_-]+/<redacted>/g'; fi
  else
    run npx --yes ctx7@latest setup --claude --oauth
    note "Context7 는 키 없이 등록됨 → Claude Code 안에서 /mcp → context7 → Authenticate 로 한 번 로그인"
  fi
  # ctx7 는 실패("Setup cancelled")에도 종료 코드 0 을 돌려주므로 결과물로 다시 판정한다.
  if [ "$CHECK_ONLY" = 0 ] && ! ctx7_present; then
    fail context7 "ctx7 setup 이 설정을 남기지 않음 (context7.com 접속 필요. 막힌 네트워크면 다른 환경에서 실행)"
  fi
fi
if [ "$CHECK_ONLY" = 0 ] && ctx7_present; then
  say "검증: npx ctx7 library next.js routing (context7.com 접속 필요)"
  npx --yes ctx7@latest library next.js routing 2>&1 | head -4 | sed 's/^/    /'
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 6. Strix (AI 침투 테스트, ~/.strix/bin/strix) =="
STRIX_BIN=""
if command -v strix >/dev/null 2>&1; then STRIX_BIN="$(command -v strix)"
elif [ -x "$HOME/.strix/bin/strix" ]; then STRIX_BIN="$HOME/.strix/bin/strix"; fi
if [ -n "$STRIX_BIN" ]; then
  ok "strix $("$STRIX_BIN" --version 2>/dev/null | awk '{print $2}') ($STRIX_BIN)"
  case ":$PATH:" in *":$HOME/.strix/bin:"*) ;; *) [ "$STRIX_BIN" = "$HOME/.strix/bin/strix" ] && note "~/.strix/bin 이 PATH 에 없음 → export PATH=\"\$HOME/.strix/bin:\$PATH\" 를 셸 설정에 추가";; esac
else
  miss strix "strix 없음"
  # 공식 설치 스크립트(README 와 동일). GitHub 릴리스 바이너리를 ~/.strix/bin 에 놓고
  # 셸 rc 파일에 PATH 를 추가하며, Docker 이미지도 당긴다.
  if [ "$CHECK_ONLY" = 1 ]; then
    say "(실행 예정) curl -sSL https://strix.ai/install | bash"
  elif curl -sSL --max-time 20 -o /dev/null https://strix.ai/install 2>/dev/null; then
    run sh -c 'curl -sSL https://strix.ai/install | bash' || fail strix "strix 설치 스크립트 실패"
  else
    # strix.ai 가 막힌 환경(프록시 등): 같은 GitHub 릴리스에서 바이너리만 받는다. rc 파일은 건드리지 않는다.
    say "strix.ai 접속 불가 → GitHub 릴리스 바이너리로 대체 설치"
    os="$(uname -s | tr '[:upper:]' '[:lower:]')"; [ "$os" = darwin ] && os=macos
    arch="$(uname -m)"; case "$arch" in aarch64|arm64) arch=arm64 ;; x86_64|amd64) arch=x86_64 ;; esac
    tag="$(git ls-remote --tags --refs https://github.com/usestrix/strix 2>/dev/null | sed -n 's|.*refs/tags/v||p' | sort -V | tail -1)"
    if [ -n "$tag" ]; then
      tmp="$(mktemp -d)"; url="https://github.com/usestrix/strix/releases/download/v${tag}/strix-${tag}-${os}-${arch}.tar.gz"
      say "\$ curl -sL $url"
      if curl -sL --max-time 300 -o "$tmp/strix.tgz" "$url" && tar -xzf "$tmp/strix.tgz" -C "$tmp"; then
        mkdir -p "$HOME/.strix/bin" && mv "$tmp/strix-${tag}-${os}-${arch}" "$HOME/.strix/bin/strix" && chmod 755 "$HOME/.strix/bin/strix" \
          && ok "strix $tag → ~/.strix/bin/strix" && note "~/.strix/bin 을 PATH 에 추가해야 'strix' 로 바로 실행 가능"
      else fail strix "릴리스 바이너리 다운로드 실패"; fi
      rm -rf "$tmp"
    else fail strix "최신 태그 조회 실패 (git ls-remote)"; fi
  fi
  note "Strix 실행에는 Docker 데몬과 LLM 키(STRIX_LLM, LLM_API_KEY 환경 변수)가 필요"
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 7. Graphify (코드베이스 지식 그래프, GSD 가 요구하는 의존성) =="
if command -v graphify >/dev/null 2>&1; then ok "graphify $(graphify --version 2>/dev/null | awk '{print $2}')"
else miss graphify-cli "graphify CLI 없음"; run uv tool install graphifyy || fail graphify-cli "uv tool install graphifyy 실패"; fi
if [ -f "$CLAUDE_HOME/skills/graphify/SKILL.md" ]; then ok "graphify 스킬 ($CLAUDE_HOME/skills/graphify)"
elif command -v graphify >/dev/null 2>&1 || [ "$CHECK_ONLY" = 1 ]; then
  miss graphify-skill "graphify 스킬 없음"
  # 전역 'graphify install' 은 스킬 복사 + ~/.claude/CLAUDE.md 등록만 한다(settings.json 훅은 --project 때만).
  backup_file "$CLAUDE_HOME/CLAUDE.md"
  run graphify install || fail graphify-skill "graphify install 실패"
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 8. Headroom (토큰 절약 프록시) =="
HEADROOM_NEW=0
if command -v headroom >/dev/null 2>&1; then ok "headroom $(headroom --version 2>/dev/null | awk '{print $3}')"
else
  miss headroom "headroom 없음"
  run uv tool install --python 3.13 "headroom-ai[proxy,mcp]" && HEADROOM_NEW=1 || fail headroom "headroom 설치 실패"
fi
if command -v headroom >/dev/null 2>&1 && { [ "$MODE" = doctor ] || [ "$HEADROOM_NEW" = 1 ]; }; then
  say "자가진단: headroom proxy --port 8787 을 잠깐 띄우고 headroom doctor 실행 후 종료"
  headroom proxy --port 8787 >/dev/null 2>&1 & HP=$!
  i=0; until curl -s -m 1 http://127.0.0.1:8787/health >/dev/null 2>&1 || [ $i -ge 30 ]; do i=$((i+1)); sleep 0.5; done
  headroom doctor 2>&1 | grep -E "proxy|version|failure" | sed 's/^/    /'
  kill "$HP" 2>/dev/null; sleep 1; kill -9 "$HP" 2>/dev/null; wait "$HP" 2>/dev/null
  say "프록시 종료함"
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 9. MCP 서버 (claude mcp) =="
add_mcp() {  # add_mcp <이름> <명령...>   이미 등록돼 있으면 건너뜀
  local name="$1"; shift
  if claude mcp get "$name" >/dev/null 2>&1; then ok "mcp $name 등록됨"; return 0; fi
  miss "mcp-$name" "mcp $name 미등록"
  run claude mcp add "$@" || fail "mcp-$name" "mcp $name 등록 실패"
}
add_mcp playwright      playwright -- npx @playwright/mcp@latest
add_mcp chrome-devtools chrome-devtools -- npx chrome-devtools-mcp@latest
add_mcp glif            --transport http glif "https://glif.app/api/mcp"
add_mcp_with_key() {  # add_mcp_with_key <이름> <환경변수명> <패키지>   키 값은 출력하지 않는다
  local name="$1" var="$2" pkg="$3"
  if claude mcp get "$name" >/dev/null 2>&1; then ok "mcp $name 등록됨"; return 0; fi
  if [ -z "${!var:-}" ]; then note "mcp $name 건너뜀: 환경 변수 $var 가 비어 있음 (키를 받은 뒤 다시 실행)"; return 0; fi
  miss "mcp-$name" "mcp $name 미등록"
  if [ "$CHECK_ONLY" = 1 ]; then say "(실행 예정) claude mcp add $name --env $var=<redacted> -- npx -y $pkg"; return 0; fi
  say "\$ claude mcp add $name --env $var=<redacted> -- npx -y $pkg"
  claude mcp add "$name" --env "$var=${!var}" -- npx -y "$pkg" >/dev/null 2>&1 || fail "mcp-$name" "mcp $name 등록 실패"
}
add_mcp_with_key perplexity PERPLEXITY_API_KEY @perplexity-ai/mcp-server
add_mcp_with_key firecrawl  FIRECRAWL_API_KEY  firecrawl-mcp
if [ "$CHECK_ONLY" = 0 ]; then say "연결 상태:"; claude mcp list 2>/dev/null | grep -E " - " | sed 's/^/    /'; fi
note "glif 는 브라우저 로그인이 필요해 'Needs authentication' 이 정상. Claude Code 안에서 /mcp → glif → Authenticate"

# ──────────────────────────────────────────────────────────────
echo; echo "== 10. Ponytail (최소 구현 강제 스킬) =="
if claude plugin list 2>/dev/null | grep -q "ponytail@ponytail"; then ok "ponytail 플러그인 설치됨"
elif ls "$CLAUDE_HOME"/skills/synced/*/ponytail/SKILL.md >/dev/null 2>&1; then
  ok "ponytail 스킬이 계정 동기화로 이미 존재 → 플러그인 설치 생략 (같은 스킬이 두 벌 되는 것을 방지)"
else
  miss ponytail "ponytail 없음"
  run claude plugin marketplace add DietrichGebert/ponytail --scope user \
    && run claude plugin install ponytail@ponytail --scope user || fail ponytail "ponytail 플러그인 설치 실패"
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 11. ECC (Everything Claude Code, 대화창에서만 설치) =="
if claude plugin list 2>/dev/null | grep -qi "ecc@ecc"; then ok "ecc 플러그인 설치됨"
else
  printf '  [없음] ecc 미설치 (자동 설치 대상 아님)\n'
  note "ECC 는 자동 설치하지 않습니다. Claude Code 대화창에 아래 두 줄을 차례로 입력하세요:"
  say "    /plugin marketplace add https://github.com/affaan-m/ECC"
  say "    /plugin install ecc@ecc"
fi

# ──────────────────────────────────────────────────────────────
echo; echo "== 결과 =="
[ -n "$NOTES" ] && printf '  안내:%s\n' "$NOTES"
if [ "$CHECK_ONLY" = 1 ]; then
  [ -z "$MISSING" ] && say "모두 설치되어 있습니다." || say "없는 항목:$MISSING  -> 설치하려면 --check 없이 다시 실행"
  exit 0
fi
if [ -z "$FAILED" ]; then
  [ -z "$MISSING" ] && say "모두 이미 설치되어 있어 아무것도 바꾸지 않았습니다." || say "새로 설치/등록:$MISSING"
  exit 0
else
  say "실패 항목:$FAILED"; exit 1
fi
