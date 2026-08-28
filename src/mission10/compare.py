"""임베딩 방식별 실험을 실행하고 성능을 비교.

가이드라인 5) 성능 비교:
- Word2Vec, FastText, GloVe 임베딩 방식을 사용했을 때의 성능을 비교하고 결과를 분석한다.
"""

from __future__ import annotations

import pandas as pd

from mission10.config import Config


def run_experiment(config: Config) -> dict:
    """설정 하나(embedding.method, model.type 등)로 전처리 -> 임베딩 -> 학습 -> 평가까지 한 번 수행한다.

    preprocessing / embeddings / dataset / model / train 모듈의 함수들을 순서대로 호출해서 조립한다.
    scripts/run_experiment.py가 이 함수를 CLI로 감싼다.

    Args:
        config: load_config로 만든 실험 설정.

    Returns:
        {"config": config, "history": {...}, "metrics": {...}} 형태의 결과 dict.
    """
    raise NotImplementedError


def compare_results(results: list[dict]) -> pd.DataFrame:
    """여러 run_experiment 결과를 하나의 비교표로 정리한다.

    Args:
        results: run_experiment가 반환한 dict들의 리스트 (예: word2vec/fasttext/glove 각각 1개씩).

    Returns:
        embedding.method(또는 model.type)를 행으로, accuracy/f1 등을 열로 갖는 DataFrame.
    """
    raise NotImplementedError
