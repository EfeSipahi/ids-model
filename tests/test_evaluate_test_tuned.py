"""Synthetic checks for the fixed tuned (v2) test evaluation.

These tests never open the real models or the real held-out test file.
"""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np

from evaluate_test_tuned import main
from test_train_logistic_regression import build_synthetic_project
from test_train_tuned import SMALL_GRIDS
from train_random_forest import read_jsonl, rows_to_xy, sha256
from train_tuned import MODELS, decide, run_experiment


def evaluate(experiment, project):
    with contextlib.redirect_stdout(io.StringIO()):
        return main(experiment, project)


class EvaluationTests(unittest.TestCase):
    def prepare(self, model):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.project = Path(directory.name)
        self.split_dir = build_synthetic_project(self.project, with_test_features=True)
        self.experiment = MODELS[model]['version']
        self.model_dir = self.project / 'models' / self.experiment
        self.run = run_experiment(self.project, self.model_dir, model, SMALL_GRIDS[model])
        self.output = self.project / 'reports' / f'{self.experiment}-test'

    def test_fixed_model_is_scored_with_the_recorded_threshold(self):
        for model in MODELS:
            with self.subTest(model=model):
                self.prepare(model)
                model_hash = sha256(self.model_dir / 'pipeline.joblib')
                result = evaluate(self.experiment, self.project)
                self.assertEqual(sha256(self.model_dir / 'pipeline.joblib'), model_hash)
                self.assertEqual(result['model_sha256'], model_hash)
                self.assertFalse(result['refit'])
                self.assertFalse(result['threshold_tuned_on_test'])
                self.assertEqual(result['threshold'], self.run['decision']['threshold'])
                self.assertEqual(result['test_records'], 4)
                for filename in ('selection_before_test.json', 'test_report.json',
                                 'test_predictions.jsonl', 'README.md'):
                    self.assertTrue((self.output / filename).is_file())
                self.assertEqual(json.loads((self.output / 'test_report.json').read_text()), result)
                predictions = read_jsonl(self.output / 'test_predictions.jsonl')
                self.assertTrue(all(row['sample_id'].startswith('test:') for row in predictions))
                x_test, y_test = rows_to_xy(read_jsonl(self.split_dir / 'test_features.jsonl'))
                scores = joblib.load(self.model_dir / 'pipeline.joblib').predict_proba(x_test)[:, 1]
                np.testing.assert_allclose(scores, [row['anomalous_score'] for row in predictions])
                np.testing.assert_array_equal(decide(scores, result['threshold']),
                                              [row['prediction'] for row in predictions])
                self.assertEqual([row['label'] for row in predictions], list(y_test))
                self.assertNotIn(str(self.project), (self.output / 'README.md').read_text(encoding='utf-8'))
                with self.assertRaises(FileExistsError):
                    evaluate(self.experiment, self.project)

    def test_tampering_stops_before_test_features_are_recorded(self):
        def replace_model(case):
            model = joblib.load(case.model_dir / 'pipeline.joblib')
            model.named_steps['drop_constant'].variances_ += 1.0
            joblib.dump(model, case.model_dir / 'pipeline.joblib')

        def change_training_data(case):
            path = case.split_dir / 'train_features.jsonl'
            path.write_text(path.read_text() + '\n', encoding='utf-8')

        def change_recorded_threshold(case):
            path = case.model_dir / 'run.json'
            run = json.loads(path.read_text(encoding='utf-8'))
            run['decision']['threshold'] = 0.99
            path.write_text(json.dumps(run), encoding='utf-8')

        def change_recorded_parameters(case):
            path = case.model_dir / 'run.json'
            run = json.loads(path.read_text(encoding='utf-8'))
            run['model_parameters']['random_state'] = 7
            path.write_text(json.dumps(run), encoding='utf-8')

        for model in MODELS:
            for tamper in (replace_model, change_training_data, change_recorded_threshold,
                           change_recorded_parameters):
                with self.subTest(model=model, tamper=tamper.__name__):
                    self.prepare(model)
                    tamper(self)
                    with self.assertRaises(ValueError):
                        evaluate(self.experiment, self.project)
                    self.assertFalse(self.output.exists())

    def test_unknown_or_mismatched_experiment_is_rejected(self):
        self.prepare('rf')
        (self.project / 'models/logreg-tuned-v2').mkdir()
        (self.project / 'models/logreg-tuned-v2/run.json').write_text(
            (self.model_dir / 'run.json').read_text(encoding='utf-8'), encoding='utf-8')
        with self.assertRaises(ValueError):
            evaluate('logreg-tuned-v2', self.project)
        self.assertFalse((self.project / 'reports').exists())

    def test_selection_is_written_before_test_features_are_read(self):
        self.prepare('logreg')
        (self.split_dir / 'test_features.jsonl').unlink()
        with self.assertRaises(FileNotFoundError):
            evaluate(self.experiment, self.project)
        selection = json.loads((self.output / 'selection_before_test.json').read_text())
        self.assertFalse(selection['refit'])
        self.assertEqual(selection['decision'], self.run['decision'])
        self.assertFalse((self.output / 'test_report.json').exists())


if __name__ == '__main__':
    unittest.main()
