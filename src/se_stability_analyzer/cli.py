"""Command-line interface for SE stability analysis."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .analysis import analyze_points, read_points
from .plotting import write_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="se-stability",
        description=(
            "Analyze near-field and far-field shielding effectiveness stability. "
            "A smaller absolute SE difference means better stability."
        ),
    )
    parser.add_argument("input_csv", type=Path, help="Input CSV file")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("se_stability_output"),
        help="Output directory (default: se_stability_output)",
    )
    parser.add_argument(
        "--target-db",
        type=float,
        default=3.0,
        help="Maximum difference considered within target (default: 3.0 dB)",
    )
    parser.add_argument(
        "--title",
        default="Near/Far-field SE stability",
        help="Title used in the SVG plot",
    )
    return parser


def write_detail_csv(result, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["frequency_ghz", "near_se_db", "far_se_db", "delta_se_db", "within_target"]
        )
        for point in result.points:
            writer.writerow(
                [
                    f"{point.frequency_ghz:.9g}",
                    f"{point.near_se_db:.9g}",
                    f"{point.far_se_db:.9g}",
                    f"{point.delta_se_db:.9g}",
                    point.delta_se_db <= result.target_delta_db,
                ]
            )


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        points = read_points(args.input_csv)
        result = analyze_points(points, args.target_db)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create output directory: {exc}", file=sys.stderr)
        return 2

    if not args.output_dir.is_dir():
        print(f"error: output path is not a directory: {args.output_dir}", file=sys.stderr)
        return 2

    summary_path = args.output_dir / "summary.json"
    detail_path = args.output_dir / "frequency_detail.csv"
    plot_path = args.output_dir / "se_stability.svg"

    try:
        summary_path.write_text(
            json.dumps(result.to_summary(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_detail_csv(result, detail_path)
        write_svg(result, plot_path, args.title)
    except OSError as exc:
        print(f"error: cannot write output files: {exc}", file=sys.stderr)
        return 2

    print(f"Frequency range: {result.min_frequency_ghz:g}-{result.max_frequency_ghz:g} GHz")
    print(f"Mean |near-far|: {result.mean_delta_db:.3f} dB")
    print(f"Maximum |near-far|: {result.max_delta_db:.3f} dB")
    print(
        f"Within {result.target_delta_db:g} dB: "
        f"{result.points_within_target}/{len(result.points)} "
        f"({result.within_target_percent:.1f}%)"
    )
    print(f"Results written to: {args.output_dir.resolve()}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
