"""평가 지표 계산.

가이드라인 5) 모델 학습 및 평가:
- 테스트 데이터에서 정확도 등 주요 평가지표를 계산한다.
"""

from __future__ import annotations


def compute_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    """정확도, 정밀도, 재현율, F1 등을 계산한다.

    Args:
        y_true: 실제 라벨 리스트.
        y_pred: 모델 예측 라벨 리스트.

    Returns:
        {"accuracy": ..., "precision": ..., "recall": ..., "f1": ...} 형태의 dict.
    """
    # TODO: sklearn.metrics (accuracy_score, precision_recall_fscore_support 등) 활용
    raise NotImplementedError
