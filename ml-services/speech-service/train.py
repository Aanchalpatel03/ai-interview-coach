import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create simple calibration for the speech service.")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("artifacts").joinpath("speech-calibration.json"))
    parser.add_argument("--target-wpm", type=float, default=135.0)
    args = parser.parse_args()

    payload = {"target_wpm": args.target_wpm}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved speech calibration to {args.output}")


if __name__ == "__main__":
    main()
