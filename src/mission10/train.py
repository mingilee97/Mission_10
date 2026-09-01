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
    model.train()
    total_loss = 0.0

    for sequences, labels in dataloader:
        sequences, labels = sequences.to(device), labels.to(device)

        optimizer.zero_grad()
        logits = model(sequences)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)


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
    model.eval()
    total_loss = 0.0
    all_labels: list[int] = []
    all_preds: list[int] = []

    for sequences, labels in dataloader:
        sequences, labels = sequences.to(device), labels.to(device)

        logits = model(sequences)
        loss = criterion(logits, labels)
        total_loss += loss.item()

        preds = torch.argmax(logits, dim=1)
        all_labels.extend(labels.cpu().tolist())
        all_preds.extend(preds.cpu().tolist())

    return total_loss / len(dataloader), all_labels, all_preds


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
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=train_cfg.lr)
    criterion = torch.nn.CrossEntropyLoss()

    history: dict[str, list[float]] = {"train_loss": [], "val_loss": []}

    for epoch in range(train_cfg.epochs):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, _, _ = evaluate(model, val_loader, criterion, device)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        print(f"epoch {epoch + 1}/{train_cfg.epochs} - train_loss: {train_loss:.4f} - val_loss: {val_loss:.4f}")

    return history
