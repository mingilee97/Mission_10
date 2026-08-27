"""Word2Vec / FastText / GloVe 임베딩 학습 및 임베딩 행렬 생성.

가이드라인 2) 임베딩 적용:
- Word2Vec, FastText, GloVe 방식으로 입력 데이터를 벡터화하여 임베딩 행렬을 생성한다.
"""

from __future__ import annotations

import numpy as np


def train_word2vec(token_lists: list[list[str]], embedding_dim: int, window: int, min_count: int):
    """gensim Word2Vec을 토큰 리스트로 학습한다.

    Args:
        token_lists: 문서별 토큰 리스트의 리스트 (문장 단위 코퍼스).
        embedding_dim: 임베딩 벡터 차원 (vector_size).
        window: 컨텍스트 윈도우 크기.
        min_count: 이 빈도 미만 단어는 학습에서 제외.

    Returns:
        학습된 gensim Word2Vec 모델.
    """
    # TODO: from gensim.models import Word2Vec; Word2Vec(token_lists, vector_size=..., window=..., min_count=...)
    raise NotImplementedError


def train_fasttext(token_lists: list[list[str]], embedding_dim: int, window: int, min_count: int):
    """gensim FastText를 토큰 리스트로 학습한다.

    Args:
        token_lists: 문서별 토큰 리스트의 리스트.
        embedding_dim: 임베딩 벡터 차원.
        window: 컨텍스트 윈도우 크기.
        min_count: 이 빈도 미만 단어는 학습에서 제외.

    Returns:
        학습된 gensim FastText 모델.
    """
    # TODO: from gensim.models import FastText; FastText(token_lists, vector_size=..., window=..., min_count=...)
    raise NotImplementedError


def load_glove(glove_path: str, embedding_dim: int) -> dict[str, np.ndarray]:
    """사전학습된 GloVe 텍스트 파일을 {단어: 벡터} 딕셔너리로 로드한다.

    Args:
        glove_path: glove.6B.100d.txt 같은 GloVe 벡터 파일 경로.
        embedding_dim: 벡터 차원 (파일의 차원과 일치해야 함).

    Returns:
        단어를 key로, numpy 벡터를 value로 갖는 dict.
    """
    # TODO: 파일을 한 줄씩 읽어 "단어 v1 v2 ... vN" 형식을 파싱
    raise NotImplementedError


def build_embedding_matrix(
    vocab: dict[str, int],
    embedding_dim: int,
    keyed_vectors,
) -> np.ndarray:
    """vocab의 각 단어 ID에 대응하는 임베딩 벡터로 이루어진 행렬을 만든다.

    Args:
        vocab: build_vocab이 만든 단어 -> ID 사전.
        embedding_dim: 임베딩 벡터 차원.
        keyed_vectors: train_word2vec/train_fasttext의 결과(.wv) 또는 load_glove의 dict.
            단어 문자열로 벡터를 조회할 수 있는 대상이면 됨.

    Returns:
        shape (vocab_size, embedding_dim) 인 numpy 행렬. 인덱스는 vocab의 ID와 일치.
        keyed_vectors에 없는 단어는 랜덤 초기화 또는 0벡터로 채운다.
    """
    # TODO: vocab 크기만큼 행렬을 만들고, 각 단어를 keyed_vectors에서 조회해 채우기
    # OOV 처리 방식(랜덤 vs 0)도 여기서 결정
    raise NotImplementedError
