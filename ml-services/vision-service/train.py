import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create simple threshold calibration for the vision service.")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("artifacts").joinpath("vision-calibration.json"))
    parser.add_argument("--posture-threshold", type=float, default=72.0)
    parser.add_argument("--eye-threshold", type=float, default=68.0)
    args = parser.parse_args()

    payload = {
        "posture_threshold": args.posture_threshold,
        "eye_threshold": args.eye_threshold,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved vision calibration to {args.output}")


if __name__ == "__main__":
    main()
