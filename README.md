# Mission_10 — LSTM 주가 예측

LSTM 기반 주가 예측 모델 미션 프로젝트.

## 미션 개요

1. 사용할 열 선택 (예: `Close`, 또는 `Open/High/Low/Close/Volume` 일부)
2. `MinMaxScaler` 등으로 0~1 범위 정규화
3. 최근 N일 시퀀스를 입력으로, 다음 날 종가(또는 상승/하락)를 라벨로 구성
4. LSTM 모델 정의 (PyTorch)
5. 학습 및 평가 (MSE/RMSE 또는 분류 정확도)
6. 예측 결과를 실제 가격과 비교 시각화

## 시작하기

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook notebooks/
```

## 구조

```
notebooks/   # 실습/미션 노트북
data/raw/    # 원본 데이터 (git에 올리지 않음)
```
