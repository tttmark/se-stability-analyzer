"""Core calculations for near/far-field SE stability."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean


REQUIRED_COLUMNS = ("frequency_ghz", "near_se_db", "far_se_db")


@dataclass(frozen=True)
class FrequencyPoint:
    frequency_ghz: float
    near_se_db: float
    far_se_db: float

    @property
    def delta_se_db(self) -> float:
        """Absolute near/far-field SE difference in dB."""
        return abs(self.near_se_db - self.far_se_db)


@dataclass(frozen=True)
class AnalysisResult:
    points: tuple[FrequencyPoint, ...]
    mean_delta_db: float
    max_delta_db: float
    rms_delta_db: float
    target_delta_db: float
    points_within_target: int

    @property
    def min_frequency_ghz(self) -> float:
        return self.points[0].frequency_ghz

    @property
    def max_frequency_ghz(self) -> float:
        return self.points[-1].frequency_ghz

    @property
    def within_target_percent(self) -> float:
        return 100.0 * self.points_within_target / len(self.points)

    def to_summary(self) -> dict[str, float | int]:
        return {
            "frequency_min_ghz": self.min_frequency_ghz,
            "frequency_max_ghz": self.max_frequency_ghz,
            "frequency_points": len(self.points),
            "mean_delta_db": self.mean_delta_db,
            "max_delta_db": self.max_delta_db,
            "rms_delta_db": self.rms_delta_db,
            "target_delta_db": self.target_delta_db,
            "points_within_target": self.points_within_target,
            "within_target_percent": self.within_target_percent,
        }


def read_points(path: str | Path) -> tuple[FrequencyPoint, ...]:
    """Read and validate frequency, near-field SE and far-field SE columns."""
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [name for name in REQUIRED_COLUMNS if name not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")

        points: list[FrequencyPoint] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                point = FrequencyPoint(
                    frequency_ghz=float(row["frequency_ghz"]),
                    near_se_db=float(row["near_se_db"]),
                    far_se_db=float(row["far_se_db"]),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value on CSV line {line_number}") from exc

            values = (point.frequency_ghz, point.near_se_db, point.far_se_db)
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"Non-finite numeric value on CSV line {line_number}")
            points.append(point)

    if not points:
        raise ValueError("The input CSV contains no data rows")

    points.sort(key=lambda point: point.frequency_ghz)
    frequencies = [point.frequency_ghz for point in points]
    if len(frequencies) != len(set(frequencies)):
        raise ValueError("Frequency values must be unique")

    return tuple(points)


def analyze_points(
    points: tuple[FrequencyPoint, ...] | list[FrequencyPoint],
    target_delta_db: float = 3.0,
) -> AnalysisResult:
    """Calculate stability metrics. Smaller delta values indicate better stability."""
    if not points:
        raise ValueError("At least one frequency point is required")
    if not math.isfinite(target_delta_db) or target_delta_db < 0:
        raise ValueError("target_delta_db must be a finite non-negative number")

    ordered_points = tuple(sorted(points, key=lambda point: point.frequency_ghz))
    deltas = [point.delta_se_db for point in ordered_points]
    return AnalysisResult(
        points=ordered_points,
        mean_delta_db=fmean(deltas),
        max_delta_db=max(deltas),
        rms_delta_db=math.sqrt(fmean(delta * delta for delta in deltas)),
        target_delta_db=target_delta_db,
        points_within_target=sum(delta <= target_delta_db for delta in deltas),
    )
