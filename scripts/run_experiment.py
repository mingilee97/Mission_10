"""실험 실행 진입점.

사용 예:
    python scripts/run_experiment.py --config configs/base.yaml
    python scripts/run_experiment.py --config configs/base.yaml --exp configs/exp/fasttext.yaml
    python scripts/run_experiment.py --config configs/base.yaml --exp configs/exp/gru.yaml

파라미터를 바꿔가며 반복 실행하고 싶다면 configs/exp/ 아래에 새 yaml을 추가하면 된다.
"""

from __future__ import annotations

import argparse

from mission10.compare import run_experiment
from mission10.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--exp", default=None, help="base 위에 덮어쓸 실험 yaml (선택)")
    args = parser.parse_args()

    config = load_config(args.config, args.exp)
    result = run_experiment(config)

    print(f"[{config.embedding.method} / {config.model.type}] metrics: {result['metrics']}")


if __name__ == "__main__":
    main()
