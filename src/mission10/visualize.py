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
    fig, ax = plt.subplots()
    epochs = range(1, len(history["train_loss"]) + 1)
    ax.plot(epochs, history["train_loss"], label="train_loss")
    ax.plot(epochs, history["val_loss"], label="val_loss")
    ax.set_xlabel("epoch")
    ax.set_ylabel("loss")
    ax.set_title(title)
    ax.legend()
    return fig


def plot_embedding_comparison(comparison_df: pd.DataFrame, metric: str = "accuracy") -> plt.Figure:
    """compare_results가 만든 비교표를 막대그래프로 그린다.

    Args:
        comparison_df: compare.compare_results의 결과.
        metric: 비교할 지표 열 이름.

    Returns:
        matplotlib Figure.
    """
    fig, ax = plt.subplots()
    labels = [" / ".join(map(str, idx)) if isinstance(idx, tuple) else str(idx) for idx in comparison_df.index]
    ax.bar(labels, comparison_df[metric])
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} by embedding/model")
    return fig
