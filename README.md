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
├── config.py         # configs/*.yaml -> dataclass 로드
├── preprocessing.py  # 로드/정제/토큰화/vocab/train-val-test 분리
├── embeddings.py     # Word2Vec/FastText 학습, GloVe 로드, 임베딩 행렬 생성
├── dataset.py        # Dataset / DataLoader / collate_fn
├── model.py          # 임베딩 레이어 + LSTM/GRU 분류기
├── train.py          # 학습 루프 (train_one_epoch / evaluate / fit)
├── metrics.py         # accuracy, precision, recall, f1 (macro)
├── compare.py         # 실험 실행(run_experiment) 및 비교표 생성
└── visualize.py       # 학습 곡선, 성능 비교 그래프

configs/
├── base.yaml          # 공통 기본 설정 (여기 값을 직접 바꿔도 됨)
└── exp/*.yaml         # base 위에 일부 값만 덮어쓰는 실험 설정 (word2vec/fasttext/glove/gru 비교용)

scripts/run_experiment.py  # 설정 하나로 전체 파이프라인 실행하는 CLI
notebooks/01_explore.ipynb # 모듈을 불러와 결과를 눈으로 확인하는 용도. 로직은 여기 넣지 않는다.
```

전 모듈 구현 완료 상태(1차 버전). 아래 "구현 요약 및 검토 포인트"에서 설계 결정과
검증 결과를 확인하고, 개선하고 싶은 부분을 논의하면서 다음 버전으로 다듬어간다.

## 구현 요약 및 검토 포인트

### 파이프라인 흐름 (`compare.run_experiment`)

```
load_raw_data (20 Newsgroups, 18846건)
  -> train_test_split_texts (2단계 stratified split: test 20% -> 남은 80%에서 val 10%)
  -> clean_text + tokenize (train/val/test 각각)
  -> build_vocab (train 토큰만 사용 — val/test 정보가 vocab에 새어들어가지 않도록)
  -> train_word2vec / train_fasttext / load_glove (embedding.method에 따라 분기)
  -> build_embedding_matrix (OOV 단어는 정규분포 랜덤 초기화, <pad>는 0벡터)
  -> build_dataloader (train/val/test)
  -> RNNTextClassifier + train.fit (매 epoch train/val loss 기록)
  -> evaluate(test) + compute_metrics (accuracy/precision/recall/f1, macro)
```

### 주요 설계 결정 (논의 대상)

| 결정 | 이유 | 재고 여지 |
|---|---|---|
| train/val/test 3-way split, vocab은 train만으로 생성 | val/test로 정보 누수 방지 | val_ratio=0.1 값 자체는 임의 선택 |
| embedding_dim 100으로 통일 (Word2Vec/FastText/GloVe 전부) | 세 방식을 공정 비교하려면 차원이 같아야 함 | GloVe는 위키피디아로 사전학습된 벡터, Word2Vec/FastText는 20 Newsgroups로 직접 학습 — **코퍼스 자체가 다르다는 한계는 여전함** |
| bidirectional RNN에서 마지막 층의 정방향+역방향 hidden을 concat해서 분류기에 입력 | 참고 베이스라인은 역방향 hidden만 썼는데(hidden[-1]), 그러면 정방향 정보가 버려짐 — 여기서는 두 방향을 모두 활용하도록 구현 | 반대로 "역방향 hidden만 쓰기"가 실제로 성능에 어떤 영향을 주는지는 직접 실험해본 적은 없음 |
| `embedding.freeze=false` (기본값) | 사전학습 임베딩도 학습 중 fine-tune됨 | GloVe/Word2Vec을 고정(freeze=true)했을 때와 비교 실험 가능 |
| OOV 단어는 정규분포 랜덤 벡터 | 0벡터로 두면 학습에 전혀 기여 못 함 | vocab 자체에 없는 매우 희귀한 단어(`<unk>`)는 여전히 정보 손실 있음 |
| metrics는 macro 평균 | 20클래스를 동등하게 취급 | 클래스별 문서 수가 불균형하면 weighted 평균이 더 적합할 수도 |

### 검증 결과 (스모크 테스트, 전체 epoch 아님)

실제 GPU(RTX 5080)에서 파이프라인이 끝까지 도는지만 확인한 결과 — 정식 비교용 수치가 아니라 "에러 없이 동작하는지"와 "loss가 감소하는지"만 본 것.

| 설정 | epoch | 소요 시간 | accuracy |
|---|---|---|---|
| word2vec / lstm | 2 | 20.3s | 0.499 |
| fasttext / lstm | 1 | 33.1s | 0.323 |
| glove / lstm | 1 | 19.0s | 0.415 |
| word2vec / gru | 1 | 17.2s | 0.367 |

epoch 수가 너무 적어 이 수치 자체로 방식 간 우열을 판단할 수는 없다. `configs/base.yaml`의
`train.epochs=10` 그대로 각 설정을 정식으로 돌려서 비교하는 게 다음 단계.

### 알려진 한계 / 다음에 볼 것

- 정식 비교 실험(10 epoch, 4개 설정 전체)을 아직 안 돌려봄
- `min_token_len`(전처리 설정)이 현재 `tokenize`/`build_vocab` 어디에서도 실제로 쓰이지 않음 — 원래 의도(너무 짧은 토큰 제거)를 구현에 반영할지 결정 필요
- GloVe OOV 비율(20 Newsgroups 어휘 중 GloVe 사전에 없는 단어 비율)을 아직 확인 안 함 — 높으면 GloVe가 불리하게 비교될 수 있음

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
