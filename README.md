# Mission_10 — 텍스트 임베딩 비교 (Word2Vec / FastText / GloVe) + RNN 분류

텍스트를 토큰화하고 Word2Vec/FastText/GloVe로 임베딩한 뒤, LSTM/GRU 기반 분류 모델의
성능을 임베딩 방식별로 비교하는 미션 프로젝트.

## 미션 가이드라인

1. **데이터 전처리** — 토큰화 수행, 훈련/테스트 세트 분리
2. **임베딩 적용** — Word2Vec, FastText, GloVe로 벡터화하여 임베딩 행렬 생성
3. **데이터셋 및 로더 구현** — PyTorch `Dataset`/`DataLoader`로 모델 입력 형태 변환
4. **모델 구현** — LSTM/GRU + 임베딩 레이어, 임베딩 방식별로 학습 가능하도록 구성
5. **학습 및 평가** — 정확도 등 지표 계산, 임베딩 방식별 성능 비교/분석
6. **성능 개선(심화)** — 전처리, 모델 구조, 하이퍼파라미터를 바꿔가며 개선

## 프로젝트 구조

이 프로젝트는 노트북에 로직을 몰아넣지 않고, 모듈로 나눠서 구현하고 파라미터는
설정 파일로 바꿔가며 실험하는 방식으로 진행한다.

```
src/mission10/
├── config.py         # configs/*.yaml -> dataclass 로드 (구현 완료, 그대로 사용)
├── preprocessing.py  # 토큰화, 훈련/테스트 분리                [TODO: 직접 구현]
├── embeddings.py     # Word2Vec/FastText 학습, GloVe 로드, 임베딩 행렬 생성  [TODO]
├── dataset.py        # Dataset / DataLoader / collate_fn        [TODO]
├── model.py          # 임베딩 레이어 + LSTM/GRU 분류기           [TODO]
├── train.py          # 학습 루프 (train_one_epoch / evaluate / fit) [TODO]
├── metrics.py         # accuracy, precision, recall, f1          [TODO]
├── compare.py         # 실험 실행 및 임베딩 방식별 비교표 생성    [TODO]
└── visualize.py       # 학습 곡선, 성능 비교 그래프              [TODO]

configs/
├── base.yaml          # 공통 기본 설정 (여기 값을 직접 바꿔도 됨)
└── exp/*.yaml         # base 위에 일부 값만 덮어쓰는 실험 설정 (word2vec/fasttext/glove/gru 비교용)

scripts/run_experiment.py  # 설정 하나로 전체 파이프라인 실행하는 CLI
notebooks/01_explore.ipynb # 모듈을 불러와 결과를 눈으로 확인하는 용도. 로직은 여기 넣지 않는다.
```

각 모듈은 함수 시그니처와 docstring, TODO만 채워져 있다. `raise NotImplementedError`가
있는 함수를 하나씩 직접 채워나가면서 진행한다.

## 파라미터를 바꿔가며 실험하기

`configs/base.yaml`의 값을 직접 바꾸거나, `configs/exp/`에 새 yaml을 만들어 일부 값만
덮어써서 비교한다.

```bash
python scripts/run_experiment.py --config configs/base.yaml
python scripts/run_experiment.py --config configs/base.yaml --exp configs/exp/fasttext.yaml
python scripts/run_experiment.py --config configs/base.yaml --exp configs/exp/glove.yaml
python scripts/run_experiment.py --config configs/base.yaml --exp configs/exp/gru.yaml
```

## 버전 관리 방식

이전 버전을 별도 파일(`v2.py`, `_old` 등)로 남기지 않는다. 파일은 항상 최신 상태
하나만 유지하고, 의미 있는 단위로 수정할 때마다 git commit으로 기록한다.

```bash
git add -A
git commit -m "feat(preprocessing): tokenize/build_vocab 구현"
git commit -m "feat(embeddings): word2vec 학습 및 임베딩 행렬 생성 구현"
git commit -m "fix(model): GRU bidirectional 옵션 반영"
```

이전 상태나 특정 시점의 코드가 궁금하면 새 파일을 만들지 말고 아래처럼 git 기록으로 확인한다.

```bash
git log --oneline                 # 지금까지의 변경 이력
git diff HEAD~3 -- src/mission10/model.py   # 3커밋 전과 현재 model.py 비교
git show <commit>:src/mission10/model.py    # 특정 커밋 시점의 파일 내용 보기
```

## 시작하기

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .          # src/mission10 을 mission10 패키지로 import 가능하게 설치
jupyter notebook notebooks/
```
