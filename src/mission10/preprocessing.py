"""텍스트 전처리 및 토큰화.

가이드라인 1) 데이터 전처리:
- 텍스트 데이터에서 토큰화를 수행한다.
- 데이터를 훈련 세트와 테스트 세트로 적절히 분리한다.
"""

from __future__ import annotations

import pandas as pd

from mission10.config import DataConfig, PreprocessingConfig


def load_raw_data(data_cfg: DataConfig) -> pd.DataFrame:
    """data_cfg.source에 따라 원본 텍스트 데이터를 읽어 ("text", "label") 두 열을 가진 DataFrame으로 반환한다.

    Args:
        data_cfg: source("20newsgroups" | "csv") 등을 포함한 설정.

    Returns:
        "text", "label" 두 열을 가진 DataFrame.
    """
    # TODO: source == "20newsgroups"인 경우
    #   sklearn.datasets.fetch_20newsgroups(subset="all", remove=("headers", "footers", "quotes"))
    #   반환된 .data(texts), .target(labels)를 DataFrame으로 변환
    # source == "csv"인 경우 data_cfg.raw_path/text_column/label_column으로 pandas 로드 (현재 미사용 경로)
    raise NotImplementedError


def clean_text(text: str, cfg: PreprocessingConfig) -> str:
    """소문자화, 특수문자 제거 등 텍스트 정제를 적용한다.

    Args:
        text: 원본 텍스트 한 건.
        cfg: lowercase, remove_special_chars 등 전처리 옵션.

    Returns:
        정제된 텍스트.
    """
    # TODO: cfg.lowercase / cfg.remove_special_chars / cfg.remove_stopwords 순서로 적용
    # remove_special_chars: re.sub(r"[^a-zA-Z\s]", "", text) 같은 정규식 활용
    # remove_stopwords: nltk.corpus.stopwords.words("english") 사용 (nltk.download("stopwords") 필요)
    raise NotImplementedError


def tokenize(text: str) -> list[str]:
    """정제된 텍스트를 토큰 리스트로 분리한다.

    Args:
        text: clean_text를 거친 텍스트.

    Returns:
        토큰(단어) 리스트.
    """
    # TODO: nltk.tokenize.word_tokenize 사용 (nltk.download("punkt"), nltk.download("punkt_tab") 필요)
    raise NotImplementedError


def build_vocab(token_lists: list[list[str]], min_count: int = 1) -> dict[str, int]:
    """토큰 리스트들로부터 단어 -> 정수 ID 사전을 만든다.

    Args:
        token_lists: 문서별 토큰 리스트의 리스트.
        min_count: 이 빈도 미만인 단어는 사전에서 제외.

    Returns:
        단어를 key로, 정수 ID를 value로 갖는 dict. 0은 padding, 1은 미등록 단어(UNK)로 예약 권장.
    """
    # TODO: 빈도 계산 -> min_count 필터 -> ID 부여 (0=<pad>, 1=<unk> 예약)
    raise NotImplementedError


def train_test_split_texts(
    texts: list[str], labels: list[int], test_ratio: float, seed: int
) -> tuple[list[str], list[str], list[int], list[int]]:
    """텍스트/라벨을 훈련/테스트 세트로 분리한다.

    Args:
        texts: 전체 텍스트 리스트.
        labels: 전체 라벨 리스트.
        test_ratio: 테스트 세트 비율 (0~1).
        seed: 재현성을 위한 랜덤 시드.

    Returns:
        (train_texts, test_texts, train_labels, test_labels)
    """
    # TODO: sklearn.model_selection.train_test_split 등 사용, stratify 고려
    raise NotImplementedError
