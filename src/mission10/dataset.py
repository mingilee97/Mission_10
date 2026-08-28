"""PyTorch Dataset / DataLoader 구성.

가이드라인 3) 데이터셋 및 로더 구현:
- PyTorch의 Dataset과 DataLoader 객체를 활용해 데이터를 처리할 수 있도록 구현한다.
- 벡터화(정수 ID화)된 데이터를 모델에 입력 가능한 형태로 변환한다.
"""

from __future__ import annotations

import torch
from torch.utils.data import DataLoader, Dataset


class TextClassificationDataset(Dataset):
    """토큰 시퀀스(정수 ID 리스트)와 라벨을 담는 Dataset."""

    def __init__(self, sequences: list[list[int]], labels: list[int]):
        """
        Args:
            sequences: 각 문서를 단어 ID 시퀀스로 변환한 리스트 (가변 길이).
            labels: 문서별 라벨 (0/1 등).
        """
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError


def collate_fn(batch: list[tuple], pad_id: int = 0, max_len: int | None = None):
    """가변 길이 시퀀스를 배치 내에서 패딩해 하나의 텐서로 만든다.

    Args:
        batch: Dataset.__getitem__ 이 반환한 (sequence, label) 튜플들의 리스트.
        pad_id: 패딩에 사용할 ID (vocab의 <pad> ID와 일치해야 함).
        max_len: 지정 시 이 길이로 자르거나 패딩. None이면 배치 내 최대 길이 사용.

    Returns:
        (padded_sequences: LongTensor[B, L], labels: LongTensor[B])
    """
    raise NotImplementedError


def build_dataloader(
    sequences: list[list[int]],
    labels: list[int],
    batch_size: int,
    shuffle: bool,
    pad_id: int = 0,
    max_len: int | None = None,
) -> DataLoader:
    """TextClassificationDataset + collate_fn을 묶어 DataLoader를 만든다.

    Args:
        sequences: 단어 ID 시퀀스 리스트.
        labels: 라벨 리스트.
        batch_size: 배치 크기.
        shuffle: 매 epoch마다 섞을지 여부 (train=True, eval=False 권장).
        pad_id: 패딩 ID.
        max_len: 시퀀스 최대 길이.

    Returns:
        구성된 DataLoader.
    """
    raise NotImplementedError
