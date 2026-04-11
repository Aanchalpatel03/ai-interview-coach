import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create simple calibration for the emotion service.")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("artifacts").joinpath("emotion-calibration.json"))
    parser.add_argument("--confidence-threshold", type=float, default=75.0)
    args = parser.parse_args()

    payload = {"confidence_threshold": args.confidence_threshold}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved emotion calibration to {args.output}")


if __name__ == "__main__":
    main()
