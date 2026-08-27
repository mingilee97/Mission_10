"""학습 루프.

가이드라인 5) 모델 학습 및 평가:
- 모델을 학습시키고, 테스트 데이터에서 성능을 평가한다.
"""

from __future__ import annotations

import torch
from torch.utils.data import DataLoader

from mission10.config import TrainConfig


def train_one_epoch(
    model: torch.nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: torch.nn.Module,
    device: torch.device,
) -> float:
    """한 epoch만큼 학습하고 평균 loss를 반환한다.

    Args:
        model: 학습할 모델.
        dataloader: 학습용 DataLoader.
        optimizer: 옵티마이저.
        criterion: 손실 함수.
        device: "cpu" 또는 "cuda".

    Returns:
        해당 epoch의 평균 학습 loss.
    """
    # TODO: model.train() -> 배치 순회하며 forward/backward/step -> 평균 loss 반환
    raise NotImplementedError


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    dataloader: DataLoader,
    criterion: torch.nn.Module,
    device: torch.device,
) -> tuple[float, list[int], list[int]]:
    """평가 데이터에 대해 loss와 예측 결과를 계산한다.

    Args:
        model: 평가할 모델.
        dataloader: 평가용 DataLoader (shuffle=False).
        criterion: 손실 함수.
        device: "cpu" 또는 "cuda".

    Returns:
        (평균 loss, 실제 라벨 리스트, 예측 라벨 리스트)
    """
    # TODO: model.eval() -> 배치 순회하며 forward만 수행, argmax로 예측 라벨 산출
    raise NotImplementedError


def fit(
    model: torch.nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    train_cfg: TrainConfig,
    device: torch.device,
) -> dict[str, list[float]]:
    """전체 학습 루프를 돌며 epoch별 학습/검증 loss를 기록한다.

    Args:
        model: 학습할 모델.
        train_loader: 학습용 DataLoader.
        val_loader: 검증용 DataLoader.
        train_cfg: epochs, lr, batch_size 등.
        device: "cpu" 또는 "cuda".

    Returns:
        {"train_loss": [...], "val_loss": [...]} 형태의 epoch별 기록.
    """
    # TODO: optimizer/criterion 생성 -> train_cfg.epochs 만큼 train_one_epoch + evaluate 반복
    raise NotImplementedError
