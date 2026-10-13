"""Synthetic checks for the fixed logistic regression test evaluation.

These tests never open the real model or the real held-out test file.
"""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np

from evaluate_test_logreg import main
from test_train_logistic_regression import build_synthetic_project
from train_logistic_regression import run_experiment
from train_random_forest import read_jsonl, rows_to_xy, sha256


def evaluate(project):
    with contextlib.redirect_stdout(io.StringIO()):
        return main(project)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.project = Path(directory.name)
        self.split_dir = build_synthetic_project(self.project, with_test_features=True)
        self.model_dir = self.project / 'models/logreg-baseline-v1'
        run_experiment(self.project, self.model_dir)
        self.output = self.project / 'reports/logreg-baseline-v1-test'

    def test_fixed_model_is_scored_on_test_without_refit(self):
        model_hash = sha256(self.model_dir / 'pipeline.joblib')
        result = evaluate(self.project)
        self.assertEqual(sha256(self.model_dir / 'pipeline.joblib'), model_hash)
        self.assertEqual(result['model_sha256'], model_hash)
        self.assertTrue(result['test_evaluated'])
        self.assertFalse(result['refit'])
        self.assertEqual(result['test_records'], 4)
        metrics = result['metrics']
        self.assertEqual(metrics['tn'] + metrics['fp'] + metrics['fn'] + metrics['tp'], 4)
        self.assertTrue(0 <= metrics['roc_auc'] <= 1)

        for filename in ('selection_before_test.json', 'test_report.json',
                         'test_predictions.jsonl', 'README.md'):
            self.assertTrue((self.output / filename).is_file())
        self.assertEqual(json.loads((self.output / 'test_report.json').read_text()), result)
        predictions = read_jsonl(self.output / 'test_predictions.jsonl')
        self.assertTrue(all(row['sample_id'].startswith('test:') for row in predictions))
        # Scores come from the saved pipeline exactly as trained.
        x_test, y_test = rows_to_xy(read_jsonl(self.split_dir / 'test_features.jsonl'))
        model = joblib.load(self.model_dir / 'pipeline.joblib')
        np.testing.assert_allclose(model.predict_proba(x_test)[:, 1],
                                   [row['anomalous_score'] for row in predictions])
        self.assertEqual([row['label'] for row in predictions], list(y_test))
        self.assertNotIn(str(self.project), (self.output / 'README.md').read_text(encoding='utf-8'))

    def test_existing_report_is_never_overwritten(self):
        evaluate(self.project)
        before = (self.output / 'test_report.json').read_bytes()
        with self.assertRaises(FileExistsError):
            evaluate(self.project)
        self.assertEqual((self.output / 'test_report.json').read_bytes(), before)

    def test_tampering_stops_before_test_features_are_recorded(self):
        def replace_model():
            model = joblib.load(self.model_dir / 'pipeline.joblib')
            model.named_steps['logreg'].coef_ += 1.0
            joblib.dump(model, self.model_dir / 'pipeline.joblib')

        def change_training_data():
            path = self.split_dir / 'train_features.jsonl'
            path.write_text(path.read_text() + '\n', encoding='utf-8')

        def change_recorded_threshold():
            path = self.model_dir / 'run.json'
            run = json.loads(path.read_text(encoding='utf-8'))
            run['decision']['threshold'] = 0.3
            path.write_text(json.dumps(run), encoding='utf-8')

        for tamper in (replace_model, change_training_data, change_recorded_threshold):
            with self.subTest(tamper=tamper.__name__):
                self.setUp()
                tamper()
                with self.assertRaises(ValueError):
                    evaluate(self.project)
                self.assertFalse(self.output.exists())

    def test_selection_is_written_before_test_features_are_read(self):
        (self.split_dir / 'test_features.jsonl').unlink()
        with self.assertRaises(FileNotFoundError):
            evaluate(self.project)
        selection = json.loads((self.output / 'selection_before_test.json').read_text())
        self.assertFalse(selection['refit'])
        self.assertEqual(selection['decision']['threshold'], 0.5)
        self.assertFalse((self.output / 'test_report.json').exists())


if __name__ == '__main__':
    unittest.main()
