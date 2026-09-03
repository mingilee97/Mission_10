"""평가 지표 계산.

가이드라인 5) 모델 학습 및 평가:
- 테스트 데이터에서 정확도 등 주요 평가지표를 계산한다.
"""

from __future__ import annotations

from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def compute_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    """정확도, 정밀도, 재현율, F1 등을 계산한다.

    Args:
        y_true: 실제 라벨 리스트.
        y_pred: 모델 예측 라벨 리스트.

    Returns:
        {"accuracy": ..., "precision": ..., "recall": ..., "f1": ...} 형태의 dict.
    """
    accuracy = accuracy_score(y_true, y_pred)
    # 20 Newsgroups는 20클래스 다중분류이므로 클래스별 지표를 단순 평균(macro)으로 합산
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}
