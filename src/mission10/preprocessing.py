"""텍스트 전처리 및 토큰화.

가이드라인 1) 데이터 전처리:
- 텍스트 데이터에서 토큰화를 수행한다.
- 데이터를 훈련 세트와 테스트 세트로 적절히 분리한다.
"""
from __future__ import annotations  # 파일에서 가장 먼저 와야 하는 특수 import (문법 규칙)

import re                            # 정규식(regex) 모듈

import pandas as pd                  # 표(DataFrame) 다루는 라이브러리
from nltk.corpus import stopwords    # 영어 불용어 목록
from sklearn.datasets import fetch_20newsgroups  # 20 Newsgroups 데이터셋 로더

from mission10.config import DataConfig, PreprocessingConfig
from nltk.tokenize import word_tokenize
from collections import Counter
from sklearn.model_selection import train_test_split


def load_raw_data(data_cfg: DataConfig) -> pd.DataFrame:
    """20 Newsgroups 데이터를 (text, label) 두 열의 DataFrame으로 반환한다."""
    news = fetch_20newsgroups(subset="all", remove=("headers", "footers", "quotes"))
    # news.data   -> 문서(텍스트) 리스트
    # news.target -> 라벨(0~19 정수) 리스트
    df = pd.DataFrame({"text": news.data, "label": news.target})  # 'Label'이 아니라 'label' (소문자로 통일 — 나중 함수들이 소문자로 찾음)
    return df


def clean_text(text: str, cfg: PreprocessingConfig) -> str:
    """소문자화, 특수문자 제거, 불용어 제거를 순서대로 적용한다."""
    if cfg.lowercase:                              # base.yaml의 preprocessing.lowercase가 True일 때만
        text = text.lower()                        # 모든 알파벳을 소문자로

    if cfg.remove_special_chars:                   # remove_special_chars가 True일 때만
        text = re.sub(r"[^a-zA-Z\s]", "", text)    # 영문자/공백이 아닌 문자(숫자, 문장부호 등)를 전부 제거

    if cfg.remove_stopwords:                        # remove_stopwords가 True일 때만
        stop_words = set(stopwords.words("english"))  # 불용어 목록을 집합으로 (in 검사 속도 때문)
        tokens = text.split()                        # 공백 기준으로 단어 리스트로 쪼갬
        tokens = [w for w in tokens if w not in stop_words]  # 불용어가 아닌 단어만 남김
        text = " ".join(tokens)                      # 다시 공백으로 이어붙여 문자열로

    return text


def tokenize(text: str) -> list[str]:
   
    tokens = word_tokenize(text) # "hello world" -> ["hello", "world"] 처럼 단어 단위로 쪼갬 (단순 split보다 구두점 처리가 똑똑함)
    return tokens

def build_vocab(token_lists: list[list[str]], min_count: int = 1) -> dict[str, int]:

    counter = Counter() # 단어별 등장 횟수를 세는 빈 카운터
    for tokens in token_lists: # 각 문서별 토큰의 리스트
        counter.update(tokens) # 그 문서의 단어들을 카운터에 누적해서 카운트

    vocab = {"<pad>": 0, "<unk>": 1}   # 0번은 패딩용, 1번은 미등록 단어(unknown)용으로 미리 예약해둔다
    next_id = 2 # 2번 부터 사용

    for word, freq in counter.items(): # counter에 쌓인 (단어, 등장횟수) 쌍을 하나씩 꺼냄
        if freq >= min_count: # min_count 이상 등장한 단어만 사전에 넣는다
            vocab[word] = next_id # 그 단어에 다음 아이디 부여
            next_id += 1

    return vocab

def train_test_split_texts(
        texts: list[str],
        labels: list[int],
        test_ratio : float,
        val_ratio : float,
        seed: int
        ):

    train_val_texts, test_texts, train_val_labels, test_labels = train_test_split(
        texts,
        labels,
        test_size = test_ratio, # 0.2
        random_state = seed,
        stratify = labels,
    )

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        train_val_texts,
        train_val_labels,
        test_size = val_ratio,
        random_state = seed,
        stratify = train_val_labels,
    )

    return train_texts, val_texts, test_texts, train_labels, val_labels, test_labels