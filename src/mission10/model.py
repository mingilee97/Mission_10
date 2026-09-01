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
            num_classes: 출력 클래스 수 (20 Newsgroups는 20. nn.CrossEntropyLoss와 함께 사용).
            pad_id: 임베딩 레이어의 padding_idx로 쓸 ID.
            freeze_embedding: True면 임베딩 가중치를 학습 중 고정.
        """
        super().__init__()
        self.rnn_type = model_cfg.type
        self.bidirectional = model_cfg.bidirectional

        self.embedding = nn.Embedding.from_pretrained(
            torch.tensor(embedding_matrix, dtype=torch.float),
            freeze=freeze_embedding,
            padding_idx=pad_id,
        )
        embedding_dim = embedding_matrix.shape[1]

        rnn_cls = nn.LSTM if model_cfg.type == "lstm" else nn.GRU
        # dropout은 num_layers>=2일 때만 레이어 사이에 적용됨 (nn.LSTM/GRU의 사양)
        self.rnn = rnn_cls(
            input_size=embedding_dim,
            hidden_size=model_cfg.hidden_size,
            num_layers=model_cfg.num_layers,
            batch_first=True,
            dropout=model_cfg.dropout if model_cfg.num_layers > 1 else 0.0,
            bidirectional=model_cfg.bidirectional,
        )

        # 양방향이면 마지막 층의 정방향/역방향 hidden을 이어붙여 쓰므로 입력 차원이 2배
        classifier_input_dim = model_cfg.hidden_size * (2 if model_cfg.bidirectional else 1)
        self.classifier = nn.Linear(classifier_input_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: LongTensor[B, L], 패딩된 단어 ID 시퀀스.

        Returns:
            FloatTensor[B, num_classes] 형태의 로짓.
        """
        embedded = self.embedding(x)  # [B, L, embedding_dim]

        if self.rnn_type == "lstm":
            _, (h_n, _) = self.rnn(embedded)
        else:
            _, h_n = self.rnn(embedded)
        # h_n: [num_layers * num_directions, B, hidden_size]

        if self.bidirectional:
            # 마지막 층의 정방향(h_n[-2])과 역방향(h_n[-1]) hidden을 이어붙임
            last_hidden = torch.cat([h_n[-2], h_n[-1]], dim=-1)
        else:
            last_hidden = h_n[-1]

        return self.classifier(last_hidden)
