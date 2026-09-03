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

`src/mission10/` 전 모듈이 1차 구현되어 있다 (PR #9 preprocessing, PR #10 나머지).
지금은 `notebooks/02_colab_pipeline.ipynb`로 Colab에서 파이프라인을 단계별로
돌려보며 문제를 찾고, 해당 모듈을 하나씩 개선하는 단계다.

알려진 점검 대상은 그 노트북의 13번 섹션과 `README.md`의 "알려진 한계"에 있다.
개선할 때도 파이프라인 순서를 따른다: `preprocessing.py` -> `embeddings.py`
-> `dataset.py` -> `model.py` -> `train.py` -> `metrics.py` -> `compare.py` -> `visualize.py`

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
