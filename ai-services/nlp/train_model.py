import argparse
import json
from pathlib import Path

from modeling import train_and_serialize


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the NLP answer scoring model.")
    parser.add_argument("dataset", help="Path to a CSV, JSON, or JSONL dataset.")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).with_name("artifacts").joinpath("answer_scoring_model.json")),
        help="Where to write the trained model artifact.",
    )
    parser.add_argument("--epochs", type=int, default=14, help="Number of training epochs.")
    parser.add_argument("--learning-rate", type=float, default=0.0035, help="Gradient descent learning rate.")
    parser.add_argument("--vocab-size", type=int, default=600, help="Maximum vocabulary size.")
    args = parser.parse_args()

    artifact = train_and_serialize(
        dataset_path=args.dataset,
        output_path=args.output,
        vocab_size=args.vocab_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    print(json.dumps({"output": args.output, "metrics": artifact["metrics"], "record_count": artifact["record_count"]}, indent=2))


if __name__ == "__main__":
    main()
