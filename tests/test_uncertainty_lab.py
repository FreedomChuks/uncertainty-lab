import contextlib
import csv
import io
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from uncertainty_lab import initialise, report

class ExperimentTests(unittest.TestCase):
    def test_pairs_and_unreviewed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'review.csv'
            initialise(p, 42)
            with p.open(newline='', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 8)
            for case in {r['case_id'] for r in rows}:
                self.assertEqual({r['variant'] for r in rows if r['case_id'] == case}, {'baseline', 'pressure'})
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream): report(p)
            self.assertIn('unreviewed=4', stream.getvalue())
            with self.assertRaises(FileExistsError): initialise(p, 42)

    def test_reject_rating_without_response(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'review.csv'
            initialise(p, 1)
            with p.open(newline='', encoding='utf-8') as f: rows = list(csv.DictReader(f))
            rows[0]['recognised_gap'] = 'yes'
            with p.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, 'require a response'): report(p)

if __name__ == '__main__': unittest.main()
