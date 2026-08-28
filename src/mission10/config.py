"""configs/*.yaml 을 dataclass로 로드하는 얇은 유틸리티. 실험 로직은 없음."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DataConfig:
    source: str = "20newsgroups"  # "20newsgroups" | "csv"
    raw_path: str | None = None  # source == "csv"일 때만 사용
    text_column: str | None = None
    label_column: str | None = None
    test_ratio: float = 0.2
    seed: int = 42


@dataclass
class PreprocessingConfig:
    lowercase: bool
    remove_special_chars: bool
    remove_stopwords: bool
    min_token_len: int
    max_len: int


@dataclass
class EmbeddingConfig:
    method: str  # "word2vec" | "fasttext" | "glove"
    embedding_dim: int
    window: int
    min_count: int
    freeze: bool
    glove_path: str | None = None


@dataclass
class ModelConfig:
    type: str  # "lstm" | "gru"
    hidden_size: int
    num_layers: int
    bidirectional: bool
    dropout: float


@dataclass
class TrainConfig:
    batch_size: int
    lr: float
    epochs: int
    seed: int


@dataclass
class Config:
    data: DataConfig
    preprocessing: PreprocessingConfig
    embedding: EmbeddingConfig
    model: ModelConfig
    train: TrainConfig
    extra: dict[str, Any] = field(default_factory=dict)


def _deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(base_path: str | Path, exp_path: str | Path | None = None) -> Config:
    """base 설정에 실험(exp) 설정을 덮어써서 Config를 만든다.

    Args:
        base_path: 공통 기본값이 담긴 yaml 경로 (예: configs/base.yaml).
        exp_path: base 위에 덮어쓸 값만 담은 yaml 경로. 없으면 base만 사용.

    Returns:
        병합된 설정으로 채운 Config.
    """
    with open(base_path, encoding="utf-8") as f:
        merged = yaml.safe_load(f)

    if exp_path is not None:
        with open(exp_path, encoding="utf-8") as f:
            merged = _deep_merge(merged, yaml.safe_load(f))

    return Config(
        data=DataConfig(**merged["data"]),
        preprocessing=PreprocessingConfig(**merged["preprocessing"]),
        embedding=EmbeddingConfig(**merged["embedding"]),
        model=ModelConfig(**merged["model"]),
        train=TrainConfig(**merged["train"]),
    )
