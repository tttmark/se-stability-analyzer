"""Dependency-free SVG output for SE curves and their absolute difference."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .analysis import AnalysisResult


WIDTH = 960
HEIGHT = 620
LEFT = 82
RIGHT = 34
TOP = 42
BOTTOM = 68


def _scale(value: float, low: float, high: float, start: float, end: float) -> float:
    if high == low:
        return (start + end) / 2
    return start + (value - low) * (end - start) / (high - low)


def _polyline(
    values: list[tuple[float, float]],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> str:
    plot_right = WIDTH - RIGHT
    plot_bottom = HEIGHT - BOTTOM
    return " ".join(
        f"{_scale(x, x_min, x_max, LEFT, plot_right):.1f},"
        f"{_scale(y, y_min, y_max, plot_bottom, TOP):.1f}"
        for x, y in values
    )


def write_svg(result: AnalysisResult, path: str | Path, title: str) -> None:
    frequencies = [point.frequency_ghz for point in result.points]
    near_values = [point.near_se_db for point in result.points]
    far_values = [point.far_se_db for point in result.points]
    deltas = [point.delta_se_db for point in result.points]

    x_min, x_max = min(frequencies), max(frequencies)
    y_min = min(0.0, min(near_values + far_values + deltas))
    y_max = max(near_values + far_values + deltas)
    padding = max((y_max - y_min) * 0.08, 1.0)
    y_min -= padding
    y_max += padding

    near_line = _polyline(
        list(zip(frequencies, near_values)), x_min, x_max, y_min, y_max
    )
    far_line = _polyline(
        list(zip(frequencies, far_values)), x_min, x_max, y_min, y_max
    )
    delta_line = _polyline(
        list(zip(frequencies, deltas)), x_min, x_max, y_min, y_max
    )
    plot_right = WIDTH - RIGHT
    plot_bottom = HEIGHT - BOTTOM

    x_ticks: list[str] = []
    y_ticks: list[str] = []
    for index in range(6):
        ratio = index / 5
        x = LEFT + ratio * (plot_right - LEFT)
        value = x_min + ratio * (x_max - x_min)
        x_ticks.append(
            f'<line x1="{x:.1f}" y1="{TOP}" x2="{x:.1f}" y2="{plot_bottom}" '
            'class="grid"/>'
            f'<text x="{x:.1f}" y="{plot_bottom + 25}" class="tick" '
            f'text-anchor="middle">{value:.2f}</text>'
        )

        y = plot_bottom - ratio * (plot_bottom - TOP)
        y_value = y_min + ratio * (y_max - y_min)
        y_ticks.append(
            f'<line x1="{LEFT}" y1="{y:.1f}" x2="{plot_right}" y2="{y:.1f}" '
            'class="grid"/>'
            f'<text x="{LEFT - 12}" y="{y + 4:.1f}" class="tick" '
            f'text-anchor="end">{y_value:.1f}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<style>
  .bg {{ fill: #ffffff; }}
  .grid {{ stroke: #e5e7eb; stroke-width: 1; }}
  .axis {{ stroke: #111827; stroke-width: 1.5; }}
  .tick {{ fill: #4b5563; font: 13px sans-serif; }}
  .label {{ fill: #111827; font: 15px sans-serif; }}
  .title {{ fill: #111827; font: bold 20px sans-serif; }}
  .legend {{ fill: #374151; font: 14px sans-serif; }}
</style>
<rect class="bg" width="100%" height="100%"/>
<text x="{WIDTH / 2}" y="28" text-anchor="middle" class="title">{escape(title)}</text>
{''.join(x_ticks)}
{''.join(y_ticks)}
<line x1="{LEFT}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" class="axis"/>
<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{plot_bottom}" class="axis"/>
<polyline points="{near_line}" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<polyline points="{far_line}" fill="none" stroke="#16a34a" stroke-width="2.5"/>
<polyline points="{delta_line}" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="7 4"/>
<text x="{(LEFT + plot_right) / 2}" y="{HEIGHT - 18}" text-anchor="middle" class="label">Frequency (GHz)</text>
<text x="22" y="{(TOP + plot_bottom) / 2}" text-anchor="middle" class="label" transform="rotate(-90 22 {(TOP + plot_bottom) / 2})">SE / difference (dB)</text>
<line x1="{LEFT + 16}" y1="{TOP + 18}" x2="{LEFT + 48}" y2="{TOP + 18}" stroke="#2563eb" stroke-width="3"/>
<text x="{LEFT + 56}" y="{TOP + 23}" class="legend">Near-field SE</text>
<line x1="{LEFT + 180}" y1="{TOP + 18}" x2="{LEFT + 212}" y2="{TOP + 18}" stroke="#16a34a" stroke-width="3"/>
<text x="{LEFT + 220}" y="{TOP + 23}" class="legend">Far-field SE</text>
<line x1="{LEFT + 344}" y1="{TOP + 18}" x2="{LEFT + 376}" y2="{TOP + 18}" stroke="#dc2626" stroke-width="3" stroke-dasharray="7 4"/>
<text x="{LEFT + 384}" y="{TOP + 23}" class="legend">|Near - Far|</text>
</svg>
"""
    Path(path).write_text(svg, encoding="utf-8")
