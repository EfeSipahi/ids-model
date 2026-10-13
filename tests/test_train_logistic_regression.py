"""Synthetic checks for the HTTP logistic regression training boundary.

These tests never open the real train, validation, or held-out test files.
The shared input contract is covered in test_train_random_forest.py.
"""
from collections import Counter
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np

from test_train_random_forest import synthetic_rows
from train_logistic_regression import make_pipeline, run_experiment, score_metrics
from train_random_forest import FEATURE_NAMES, rows_to_xy


class PipelineTests(unittest.TestCase):
    def test_preprocessing_is_learned_only_from_training(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline().fit(x_train, y_train)
        selector = pipeline.named_steps['drop_constant']
        scaler = pipeline.named_steps['scale']
        support, mean, scale = selector.get_support().copy(), scaler.mean_.copy(), scaler.scale_.copy()
        self.assertFalse(support[list(FEATURE_NAMES).index('path_length')])

        x_validation = x_train.iloc[:4].copy() * 50
        x_validation['path_length'] = [1.0, 1000.0, 3.0, 9999.0]
        self.assertEqual(len(pipeline.predict(x_validation)), 4)
        np.testing.assert_array_equal(selector.get_support(), support)
        np.testing.assert_array_equal(scaler.mean_, mean)
        np.testing.assert_array_equal(scaler.scale_, scale)

    def test_training_features_are_standardized_after_log1p(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline().fit(x_train, y_train)
        transformed = pipeline[:-1].transform(x_train)
        kept = pipeline.named_steps['drop_constant'].get_feature_names_out()
        self.assertEqual(transformed.shape, (len(x_train), len(kept)))
        np.testing.assert_allclose(transformed.mean(axis=0), 0, atol=1e-9)
        np.testing.assert_allclose(transformed.std(axis=0), 1, atol=1e-9)
        expected = np.log1p(x_train[kept].to_numpy())
        np.testing.assert_allclose(pipeline.named_steps['scale'].mean_, expected.mean(axis=0))

    def test_scores_are_probabilities_and_match_threshold_rule(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline().fit(x_train, y_train)
        scores = pipeline.predict_proba(x_train * 1000)[:, 1]
        self.assertTrue(((scores >= 0) & (scores <= 1)).all())
        scores = pipeline.predict_proba(x_train)[:, 1]
        np.testing.assert_array_equal(pipeline.predict(x_train), (scores > 0.5).astype(int))

    def test_fitted_pipeline_rejects_reordered_and_nonfinite_validation(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline().fit(x_train, y_train)
        invalid_inputs = {'reordered': x_train.iloc[:3, ::-1].copy()}
        for value in (float('nan'), float('inf')):
            invalid = x_train.iloc[:3].copy()
            invalid.iloc[0, 0] = value
            invalid_inputs[str(value)] = invalid
        for case, invalid in invalid_inputs.items():
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    pipeline.predict(invalid)

    def test_saved_pipeline_roundtrip_preserves_predictions(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline().fit(x_train, y_train)
        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / 'pipeline.joblib'
            joblib.dump(pipeline, model_path)
            restored = joblib.load(model_path)
        np.testing.assert_array_equal(pipeline.predict(x_train), restored.predict(x_train))
        np.testing.assert_allclose(pipeline.predict_proba(x_train), restored.predict_proba(x_train))
        np.testing.assert_array_equal(pipeline.feature_names_in_, restored.feature_names_in_)


class MetricsTests(unittest.TestCase):
    def test_roc_auc_uses_scores_not_thresholded_predictions(self):
        # Every anomalous score is above every normal score, so ranking is
        # perfect (AUC 1) although the 0.5 threshold misses one anomalous row.
        y = [0, 0, 1, 1]
        scores = np.array([0.1, 0.2, 0.4, 0.9])
        result = score_metrics(y, (scores > 0.5).astype(int), scores)
        self.assertEqual(result['roc_auc'], 1.0)
        self.assertEqual([result[key] for key in ('tn', 'fp', 'fn', 'tp')], [2, 0, 1, 1])
        self.assertAlmostEqual(result['recall'], 0.5)


def build_synthetic_project(project, with_test_features=False):
    """Writes a tiny content-split-v1 project; test features only on request."""
    split_dir = project / 'data/processed/http-mini-splits-v1'
    split_dir.mkdir(parents=True)
    assignments = []
    summaries = {}
    for split, count in [('train', 24), ('validation', 8), ('test', 4)]:
        rows = synthetic_rows(count)
        members = []
        for index, row in enumerate(rows):
            row['sample_id'] = f'{split}:{index}'
            row['group_id'] = f'{split}-group:{index}'
            if split == 'validation':
                # This feature is constant in train and varying only
                # in validation: accidental refitting would retain it.
                row['features']['path_length'] = float(index + 100)
            members.append({
                'sample_id': row['sample_id'],
                'group_id': row['group_id'],
                'split': split,
                'label': row['label'],
                'method': 'GET' if index % 2 == 0 else 'POST',
                'pinned_to_train': False,
            })
        assignments.extend(members)
        summaries[split] = {
            'records': count,
            'groups': count,
            'labels': dict(Counter(str(row['label']) for row in members)),
            'label_method': dict(Counter(f"{row['label']}/{row['method']}" for row in members)),
        }
        if split != 'test' or with_test_features:
            (split_dir / f'{split}_features.jsonl').write_text(
                ''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
    (split_dir / 'assignments.jsonl').write_text(
        ''.join(json.dumps(row) + '\n' for row in assignments), encoding='utf-8')

    # Sources are hashed solely for provenance, never parsed for X/y.
    source_hashes = {}
    for key, relative in [
        ('input_sha256', 'data/http-mini/requests.jsonl'),
        ('features_sha256', 'data/processed/http-mini-features-v1/features.jsonl'),
    ]:
        source = project / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        payload = b'synthetic provenance bytes; deliberately not JSON\n'
        source.write_bytes(payload)
        source_hashes[key] = hashlib.sha256(payload).hexdigest()
    (split_dir / 'split_report.json').write_text(json.dumps({
        'version': 'content-split-v1',
        'records': len(assignments),
        'splits': summaries,
        **source_hashes,
    }), encoding='utf-8')
    return split_dir


class ExperimentBoundaryTests(unittest.TestCase):
    def test_experiment_never_reads_test_or_fits_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            split_dir = build_synthetic_project(project)

            original_open = Path.open

            def forbid_test_features(path, *args, **kwargs):
                if path.name == 'test_features.jsonl':
                    raise AssertionError('Held-out test features must not be opened')
                return original_open(path, *args, **kwargs)

            output_dir = project / 'new-model'
            with patch.object(Path, 'open', forbid_test_features):
                run = run_experiment(project, output_dir)
            self.assertFalse((split_dir / 'test_features.jsonl').exists())
            self.assertEqual(run['version'], 'logreg-baseline-v1')
            self.assertFalse(run['test_features_loaded'])
            self.assertFalse(run['test_evaluated'])
            self.assertEqual(run['training_records'], 24)
            self.assertEqual(run['validation_records'], 8)
            self.assertIn('path_length', run['dropped_constant_features'])
            self.assertEqual(list(run['coefficients']), run['retained_feature_order'])
            self.assertNotIn('path_length', run['coefficients'])
            metrics = run['validation']['logistic_regression']
            self.assertTrue(0 <= metrics['roc_auc'] <= 1)
            self.assertEqual(metrics['tn'] + metrics['fp'] + metrics['fn'] + metrics['tp'], 8)
            for filename in ('pipeline.joblib', 'run.json', 'validation_predictions.jsonl',
                             'validation_errors.jsonl'):
                self.assertTrue((output_dir / filename).is_file())
            restored = joblib.load(output_dir / 'pipeline.joblib')
            predictions = [json.loads(line) for line in
                           (output_dir / 'validation_predictions.jsonl').read_text().splitlines()]
            self.assertEqual(len(predictions), 8)
            self.assertTrue(all(row['sample_id'].startswith('validation:') for row in predictions))
            # The saved model reproduces the recorded scores without refitting.
            x_validation, _ = rows_to_xy(
                [json.loads(line) for line in (split_dir / 'validation_features.jsonl').read_text().splitlines()])
            np.testing.assert_allclose(restored.predict_proba(x_validation)[:, 1],
                                       [row['anomalous_score'] for row in predictions])
            with self.assertRaises(FileExistsError):
                run_experiment(project, output_dir)


if __name__ == '__main__':
    unittest.main()
