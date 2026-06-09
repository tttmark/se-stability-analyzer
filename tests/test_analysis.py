import csv
import tempfile
import unittest
from pathlib import Path

from se_stability_analyzer.analysis import FrequencyPoint, analyze_points, read_points


class AnalysisTests(unittest.TestCase):
    def test_metrics_and_target_count(self):
        result = analyze_points(
            [
                FrequencyPoint(2.0, 20.0, 18.0),
                FrequencyPoint(1.0, 15.0, 14.0),
                FrequencyPoint(3.0, 25.0, 21.0),
            ],
            target_delta_db=2.0,
        )

        self.assertEqual([point.frequency_ghz for point in result.points], [1.0, 2.0, 3.0])
        self.assertAlmostEqual(result.mean_delta_db, 7 / 3)
        self.assertEqual(result.max_delta_db, 4.0)
        self.assertEqual(result.points_within_target, 2)
        self.assertAlmostEqual(result.within_target_percent, 200 / 3)

    def test_rejects_negative_target(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            analyze_points([FrequencyPoint(1.0, 10.0, 9.0)], -1.0)

    def test_read_points_accepts_bom_and_sorts_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["frequency_ghz", "near_se_db", "far_se_db"])
                writer.writerow([2.0, 20.0, 18.0])
                writer.writerow([1.0, 15.0, 14.0])

            points = read_points(path)

        self.assertEqual([point.frequency_ghz for point in points], [1.0, 2.0])

    def test_read_points_rejects_duplicate_frequency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_text(
                "frequency_ghz,near_se_db,far_se_db\n"
                "1,10,9\n"
                "1,11,8\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unique"):
                read_points(path)


if __name__ == "__main__":
    unittest.main()
