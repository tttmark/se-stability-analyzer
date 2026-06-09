import json
import tempfile
import unittest
from pathlib import Path

from se_stability_analyzer.cli import run


class CliTests(unittest.TestCase):
    def test_cli_generates_all_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.csv"
            output_path = root / "result"
            input_path.write_text(
                "frequency_ghz,near_se_db,far_se_db\n"
                "1,20,19\n"
                "2,25,22\n",
                encoding="utf-8",
            )

            exit_code = run(
                [str(input_path), "--output-dir", str(output_path), "--target-db", "2"]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_path / "frequency_detail.csv").is_file())
            self.assertTrue((output_path / "se_stability.svg").is_file())
            summary = json.loads((output_path / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["mean_delta_db"], 2.0)
            self.assertEqual(summary["points_within_target"], 1)

    def test_cli_rejects_output_path_that_is_a_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.csv"
            output_path = root / "occupied"
            input_path.write_text(
                "frequency_ghz,near_se_db,far_se_db\n1,20,19\n",
                encoding="utf-8",
            )
            output_path.write_text("not a directory", encoding="utf-8")

            exit_code = run([str(input_path), "--output-dir", str(output_path)])

            self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
