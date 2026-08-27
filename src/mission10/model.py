"""임베딩 레이어 + LSTM/GRU 기반 텍스트 분류 모델.

가이드라인 4) 모델 구현:
- LSTM, GRU 등 RNN 기반의 딥러닝 모델을 구현한다.
- 임베딩 레이어를 추가해 입력 데이터와 임베딩 벡터를 연결한다.
- 각 임베딩 방식(Word2Vec, FastText, GloVe)에 대해 모델을 학습할 수 있도록 설정한다.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from mission10.config import ModelConfig


class RNNTextClassifier(nn.Module):
    """사전학습 임베딩 행렬로 초기화한 임베딩 레이어 + LSTM/GRU 분류기."""

    def __init__(
        self,
        embedding_matrix: np.ndarray,
        model_cfg: ModelConfig,
        num_classes: int,
        pad_id: int = 0,
        freeze_embedding: bool = False,
    ):
        """
        Args:
            embedding_matrix: build_embedding_matrix가 만든 (vocab_size, embedding_dim) 행렬.
            model_cfg: type("lstm"/"gru"), hidden_size, num_layers, bidirectional, dropout.
            num_classes: 출력 클래스 수 (이진 분류면 2, 또는 1로 두고 BCE 사용).
            pad_id: 임베딩 레이어의 padding_idx로 쓸 ID.
            freeze_embedding: True면 임베딩 가중치를 학습 중 고정.
        """
        super().__init__()
        # TODO:
        # 1. nn.Embedding.from_pretrained(embedding_matrix, freeze=freeze_embedding, padding_idx=pad_id)
        # 2. model_cfg.type에 따라 nn.LSTM 또는 nn.GRU 생성 (batch_first=True)
        # 3. 마지막 hidden state -> nn.Linear(..., num_classes) 분류 헤드
        raise NotImplementedError

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: LongTensor[B, L], 패딩된 단어 ID 시퀀스.

        Returns:
            FloatTensor[B, num_classes] 형태의 로짓.
        """
        # TODO: embedding -> rnn -> 마지막 timestep(또는 hidden state) -> classifier
        raise NotImplementedError
