"""임베딩 방식별 실험을 실행하고 성능을 비교.

가이드라인 5) 성능 비교:
- Word2Vec, FastText, GloVe 임베딩 방식을 사용했을 때의 성능을 비교하고 결과를 분석한다.
"""

from __future__ import annotations

import pandas as pd
import torch

from mission10 import dataset as dataset_module
from mission10 import embeddings as embeddings_module
from mission10 import metrics as metrics_module
from mission10 import preprocessing as preprocessing_module
from mission10 import train as train_module
from mission10.config import Config
from mission10.model import RNNTextClassifier


def _build_keyed_vectors(config: Config, token_lists: list[list[str]]):
    """embedding.method에 따라 word2vec/fasttext를 학습하거나 glove를 로드해서 반환한다."""
    if config.embedding.method == "word2vec":
        emb_model = embeddings_module.train_word2vec(
            token_lists, config.embedding.embedding_dim, config.embedding.window, config.embedding.min_count
        )
        return emb_model.wv
    if config.embedding.method == "fasttext":
        emb_model = embeddings_module.train_fasttext(
            token_lists, config.embedding.embedding_dim, config.embedding.window, config.embedding.min_count
        )
        return emb_model.wv
    if config.embedding.method == "glove":
        return embeddings_module.load_glove(config.embedding.glove_path, config.embedding.embedding_dim)
    raise ValueError(f"알 수 없는 embedding.method: {config.embedding.method}")


def run_experiment(config: Config) -> dict:
    """설정 하나(embedding.method, model.type 등)로 전처리 -> 임베딩 -> 학습 -> 평가까지 한 번 수행한다.

    preprocessing / embeddings / dataset / model / train 모듈의 함수들을 순서대로 호출해서 조립한다.
    scripts/run_experiment.py가 이 함수를 CLI로 감싼다.

    Args:
        config: load_config로 만든 실험 설정.

    Returns:
        {"config": config, "history": {...}, "metrics": {...}} 형태의 결과 dict.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    df = preprocessing_module.load_raw_data(config.data)
    texts, labels = df["text"].tolist(), df["label"].tolist()

    (
        train_texts, val_texts, test_texts,
        train_labels, val_labels, test_labels,
    ) = preprocessing_module.train_test_split_texts(
        texts, labels, config.data.test_ratio, config.data.val_ratio, config.data.seed
    )

    def to_tokens(raw_texts: list[str]) -> list[list[str]]:
        return [preprocessing_module.tokenize(preprocessing_module.clean_text(t, config.preprocessing)) for t in raw_texts]

    train_tokens = to_tokens(train_texts)
    val_tokens = to_tokens(val_texts)
    test_tokens = to_tokens(test_texts)

    # vocab은 train 데이터만으로 만든다 (val/test 정보가 새어들어가지 않도록)
    vocab = preprocessing_module.build_vocab(train_tokens, min_count=config.embedding.min_count)

    keyed_vectors = _build_keyed_vectors(config, train_tokens)
    embedding_matrix = embeddings_module.build_embedding_matrix(vocab, config.embedding.embedding_dim, keyed_vectors)

    def to_sequences(token_lists: list[list[str]]) -> list[list[int]]:
        unk_id = vocab["<unk>"]
        return [[vocab.get(tok, unk_id) for tok in tokens] for tokens in token_lists]

    train_loader = dataset_module.build_dataloader(
        to_sequences(train_tokens), train_labels, config.train.batch_size, shuffle=True, max_len=config.preprocessing.max_len
    )
    val_loader = dataset_module.build_dataloader(
        to_sequences(val_tokens), val_labels, config.train.batch_size, shuffle=False, max_len=config.preprocessing.max_len
    )
    test_loader = dataset_module.build_dataloader(
        to_sequences(test_tokens), test_labels, config.train.batch_size, shuffle=False, max_len=config.preprocessing.max_len
    )

    num_classes = len(set(labels))
    rnn_model = RNNTextClassifier(
        embedding_matrix,
        config.model,
        num_classes,
        pad_id=vocab["<pad>"],
        freeze_embedding=config.embedding.freeze,
    ).to(device)

    history = train_module.fit(rnn_model, train_loader, val_loader, config.train, device)

    criterion = torch.nn.CrossEntropyLoss()
    _, y_true, y_pred = train_module.evaluate(rnn_model, test_loader, criterion, device)
    test_metrics = metrics_module.compute_metrics(y_true, y_pred)

    return {"config": config, "history": history, "metrics": test_metrics}


def compare_results(results: list[dict]) -> pd.DataFrame:
    """여러 run_experiment 결과를 하나의 비교표로 정리한다.

    Args:
        results: run_experiment가 반환한 dict들의 리스트 (예: word2vec/fasttext/glove 각각 1개씩).

    Returns:
        embedding.method(또는 model.type)를 행으로, accuracy/f1 등을 열로 갖는 DataFrame.
    """
    rows = []
    for result in results:
        config = result["config"]
        row = {"embedding": config.embedding.method, "model": config.model.type}
        row.update(result["metrics"])
        rows.append(row)

    return pd.DataFrame(rows).set_index(["embedding", "model"])
