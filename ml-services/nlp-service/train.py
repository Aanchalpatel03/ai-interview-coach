import argparse
from pathlib import Path

from inference import build_calibration_artifact, load_records, save_artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Build calibration artifacts for the NLP service.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("artifacts").joinpath("nlp-calibration.json"))
    args = parser.parse_args()

    records = load_records(args.dataset)
    artifact = build_calibration_artifact(records)
    save_artifact(args.output, artifact)
    print(f"Saved calibration artifact to {args.output}")


if __name__ == "__main__":
    main()
