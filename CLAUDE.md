# 프로젝트 컨텍스트 (AI 어시스턴트용)

이 파일은 Claude Code가 이 저장소에서 작업할 때 참고하는 규약이다.
사람이 읽는 안내는 `README.md` 쪽이 더 자세하다.

## 프로젝트 목적

텍스트를 토큰화 -> Word2Vec/FastText/GloVe로 임베딩 -> LSTM/GRU 분류 모델 학습까지
직접 구현하며 배우는 미션. **결과(정확도)보다 구현 과정 자체가 목적**이다.

## 진행 방식 (중요)

- 사용자는 `ipynb`에 로직을 몰아넣지 않고, `src/mission10/` 안의 `.py` 모듈을
  하나씩 직접 구현해나가길 원한다. Claude는 사용자가 막힌 부분을 함께 상의하고
  검토하는 역할이며, 요청 없이 TODO 함수 본문을 대신 전부 구현해버리지 않는다.
- 하이퍼파라미터는 `configs/base.yaml` / `configs/exp/*.yaml`로 관리한다.
  코드에 값을 하드코딩하지 않는다.
- **이전 버전은 파일로 남기지 않는다.** `model_v2.py`, `_old`, `_backup` 같은
  파일을 만들지 말 것. 파일은 항상 최신 상태 하나만 유지하고, 의미 있는 변경
  단위로 git commit을 남겨서 히스토리로 추적한다.
- 노트북(`notebooks/`)은 모듈을 불러와 결과를 확인하는 탐색용으로만 쓴다.

## 현재 상태

`src/mission10/` 각 모듈은 함수 시그니처 + docstring(Args/Returns) + TODO 주석만
있고 본문은 `raise NotImplementedError` 상태다. `config.py`만 완성되어 있다.

구현 순서 권장: `preprocessing.py` -> `embeddings.py` -> `dataset.py` -> `model.py`
-> `train.py` -> `metrics.py` -> `compare.py` -> `visualize.py`

## 코드 규약

- 타입 힌트를 붙이고, 공개 함수에는 docstring(Args/Returns)을 쓴다.
- 주석은 **왜**를 쓴다. 무엇을 하는지는 코드가 말한다.
- 새 실험을 추가할 때는 `configs/exp/`에 base 위에 덮어쓸 값만 담은 yaml을 추가한다.

## 자주 쓰는 명령

```bash
python scripts/run_experiment.py --config configs/base.yaml
python scripts/run_experiment.py --config configs/base.yaml --exp configs/exp/fasttext.yaml
git log --oneline
git show <commit>:src/mission10/model.py   # 특정 커밋 시점 파일 확인
```

## 세션 시작 시 도구 확인 (모든 환경 공통)

이 프로젝트는 아래 도구를 전제로 한다. 앞의 네 개 스킬은 `.claude/skills/`에 커밋되어
git으로 따라오지만, **나머지는 컴퓨터마다 따로 설치**되어 있어야 한다(데스크톱, 노트북,
웹 컨테이너가 각각 다르다).

| 세트 | 항목 |
|---|---|
| 스킬 | agent-browser, find-skills, design-taste-frontend, mcp-builder (git), GSD, agent-browser CLI |
| 바이브 코딩 도구 | Context7(ctx7), Strix, Graphify, Headroom, Ponytail, ECC |
| MCP 서버 | playwright, chrome-devtools, glif, perplexity(키 필요), firecrawl(키 필요) |

- 세션을 시작하면 작업에 들어가기 전에 먼저 `bash scripts/setup_claude_skills.sh --check`를
  실행해 이 컴퓨터에 무엇이 빠졌는지 확인한다.
- 빠진 항목이 있으면 `bash scripts/setup_claude_skills.sh`를 실행해 **없는 것만** 설치한다.
  이미 있는 항목은 스크립트가 건너뛰므로 중복 설치되지 않는다.
- 중복 방지 규칙은 스크립트 머리말에 적혀 있다. Ponytail 플러그인의 스킬은 계정 동기화
  스킬과 같지만 항상 켜짐 훅과 강도 조절을 더하므로 플러그인 목록에 없을 때만 설치한다.
  ECC는 공식 터미널 명령으로 설치하되 설치 뒤 `npx ecc-universal setup`이나 훅 복사를
  추가로 하지 않는다(스킬·훅 중복). ECC가 함께 올리는 chrome-devtools MCP는 직접 등록한
  것과 겹치므로 플러그인 쪽을 끈다. Graphify는 GSD가 요구하는 의존성이므로 중복이 아니다.
- GSD 설치는 `~/.claude/settings.json`에, `graphify install`은 `~/.claude/CLAUDE.md`에
  내용을 추가한다. 스크립트가 설치 전에 날짜가 붙은 백업 사본을 남기므로, 설치 후
  사용자에게 백업 위치를 알려준다. GSD를 새로 설치했다면 Claude Code 재시작이 필요하다.
- API 키가 필요한 항목(perplexity, firecrawl, Strix의 LLM 키)은 환경 변수에 키가 있을 때만
  진행하고, 키 값은 어떤 경우에도 화면이나 로그에 출력하지 않는다. `.env`는 읽지 않는다.
- 네트워크가 막혀 실패한 항목(예: 웹 컨테이너에서 context7.com, strix.ai)은 반복 시도하지
  말고 "다른 환경에서 실행"으로 보고한다. agent-browser의 Chrome 다운로드가 막히면
  `AGENT_BROWSER_EXECUTABLE_PATH`에 기존 Chromium 경로를 지정해서 쓴다.
- 확인 결과와 새로 설치한 항목은 사용자에게 짧게 보고한다. 모두 설치되어 있으면
  한 줄로만 알리고 바로 작업으로 넘어간다.
