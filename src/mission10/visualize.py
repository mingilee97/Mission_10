"""학습 곡선 및 임베딩 방식별 성능 비교 시각화."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_training_curves(history: dict[str, list[float]], title: str = "") -> plt.Figure:
    """train_loss / val_loss 곡선을 그린다.

    Args:
        history: train.fit이 반환한 {"train_loss": [...], "val_loss": [...]}.
        title: 그래프 제목 (예: 임베딩 방식 이름).

    Returns:
        matplotlib Figure.
    """
    raise NotImplementedError


def plot_embedding_comparison(comparison_df: pd.DataFrame, metric: str = "accuracy") -> plt.Figure:
    """compare_results가 만든 비교표를 막대그래프로 그린다.

    Args:
        comparison_df: compare.compare_results의 결과.
        metric: 비교할 지표 열 이름.

    Returns:
        matplotlib Figure.
    """
    raise NotImplementedError
