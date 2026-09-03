"""Word2Vec / FastText / GloVe 임베딩 학습 및 임베딩 행렬 생성.

가이드라인 2) 임베딩 적용:
- Word2Vec, FastText, GloVe 방식으로 입력 데이터를 벡터화하여 임베딩 행렬을 생성한다.
"""

from __future__ import annotations

import numpy as np
from gensim.models import Word2Vec
from gensim.models import FastText


def train_word2vec(token_lists: list[list[str]], embedding_dim: int, window: int, min_count: int):
    model = Word2Vec(
        sentences = token_lists, #문서별 토큰 리스트의 리스트
        vector_size = embedding_dim, #단어 하나를 몇 차원 벡터로 표현할지
        window = window,  # 한 단어 기준 앞 뒤로 몇 개 단어까지를 문맥으로볼지
        min_count = min_count, # 최소 카운트 이상 등장한 단어만 학습
    )

    return model

def train_fasttext(token_lists: list[list[str]], embedding_dim: int, window: int, min_count: int):
    model = FastText(
        sentences = token_lists, # 문서별 토큰 리스트의 리스트
        vector_size = embedding_dim, # 사전 정의된 벡터 사이즈
        window = window,
        min_count = min_count,
    )

    return model


def load_glove(glove_path: str, embedding_dim: int) -> dict[str, np.ndarray]:
    embeddings_dict = {}
    with open(glove_path, encoding = 'utf-8') as f: # 파일 열기
        for line in f:
            values = line.split() # 공백 기준 분리
            word = values[0] # 첫 번째 값이 단어
            vector = np.asarray(values[1:], dtype = 'float32') # 2~100은 임베딩
            embeddings_dict[word] = vector

    return embeddings_dict


def build_embedding_matrix(
    vocab: dict[str, int],
    embedding_dim: int,
    keyed_vectors,
) -> np.ndarray:
    """vocab의 각 단어 ID에 대응하는 임베딩 벡터로 이루어진 행렬을 만든다."""
    vocab_size = len(vocab)
    matrix = np.random.normal(size=(vocab_size, embedding_dim)).astype("float32")
    matrix[0] = np.zeros(embedding_dim)  # <pad>는 항상 0벡터

    for word, idx in vocab.items():
        if word in keyed_vectors:
            matrix[idx] = keyed_vectors[word]

    return matrix