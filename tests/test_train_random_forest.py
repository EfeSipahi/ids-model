"""Synthetic checks for the HTTP Random Forest training boundary.

These tests never open the real train, validation, or held-out test files.
"""
import copy
from collections import Counter
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np

from extract_features import BASIC_FEATURES, PATTERN_FEATURES
from train_random_forest import (
    FEATURE_NAMES,
    binary_metrics,
    make_pipeline,
    rows_to_xy,
    run_experiment,
)


def synthetic_rows(count=24):
    rows = []
    for i in range(count):
        # Reverse insertion order deliberately: model order must come from the
        # explicit feature contract, not each input dictionary's order.
        features = {
            name: float((i + position) % 11)
            for position, name in reversed(list(enumerate(FEATURE_NAMES)))
        }
        features['path_length'] = 7.0
        rows.append({
            'features': features,
            'label': i % 2,
            'sample_id': f'synthetic:{i}',
            'group_id': f'group:{i}',
            'content_group': 'metadata-never-input',
            'source_file': 'synthetic.txt',
            'parse_status': {'body': 'parsed'},
        })
    return rows


class InputContractTests(unittest.TestCase):
    def test_metadata_excluded_and_feature_order_is_explicit(self):
        rows = synthetic_rows()
        original = copy.deepcopy(rows)
        x, y = rows_to_xy(rows)
        self.assertEqual(tuple(FEATURE_NAMES), tuple(BASIC_FEATURES + PATTERN_FEATURES))
        self.assertEqual(list(x.columns), list(FEATURE_NAMES))
        self.assertEqual(x.shape, (len(rows), len(FEATURE_NAMES)))
        np.testing.assert_array_equal(y, [row['label'] for row in rows])
        for name in FEATURE_NAMES:
            np.testing.assert_array_equal(x[name], [row['features'][name] for row in rows])
        self.assertEqual(rows, original)

        changed = copy.deepcopy(rows)
        for index, row in enumerate(changed):
            row['sample_id'] = f'different-id:{index}'
            row['group_id'] = 'different-group'
            row['content_group'] = 99999
            row['source_file'] = 'different-source.txt'
            row['parse_status'] = {'body': 'unsupported'}
            row['untrusted_new_metadata'] = {'label_hint': row['label']}
        changed_x, changed_y = rows_to_xy(changed)
        np.testing.assert_array_equal(x, changed_x)
        np.testing.assert_array_equal(y, changed_y)

    def test_missing_feature_and_unexpected_feature_are_rejected(self):
        for mutation in ('missing', 'unexpected'):
            with self.subTest(mutation=mutation):
                rows = synthetic_rows()
                if mutation == 'missing':
                    del rows[0]['features'][FEATURE_NAMES[0]]
                else:
                    rows[0]['features']['source_file_encoded'] = 1
                with self.assertRaises((ValueError, TypeError)):
                    rows_to_xy(rows)

    def test_missing_nonnumeric_and_nonfinite_values_are_rejected(self):
        for value in (None, 'not-a-number', float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value):
                rows = synthetic_rows()
                rows[0]['features'][FEATURE_NAMES[0]] = value
                with self.assertRaises((ValueError, TypeError)):
                    rows_to_xy(rows)

    def test_invalid_labels_are_rejected(self):
        for label in (-1, 2, 0.5, None, '1', True):
            with self.subTest(label=label):
                rows = synthetic_rows()
                rows[0]['label'] = label
                with self.assertRaises((ValueError, TypeError)):
                    rows_to_xy(rows)


class TrainingBoundaryTests(unittest.TestCase):
    def test_constant_feature_mask_is_learned_only_from_training(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline()
        pipeline.fit(x_train, y_train)
        selector = pipeline.named_steps['drop_constant']
        original_support = selector.get_support().copy()
        original_variances = selector.variances_.copy()
        self.assertFalse(original_support[list(FEATURE_NAMES).index('path_length')])

        x_validation = x_train.iloc[:4].copy()
        x_validation['path_length'] = [1.0, 1000.0, 3.0, 9999.0]
        transformed = pipeline[:-1].transform(x_validation)
        predictions = pipeline.predict(x_validation)
        self.assertEqual(len(predictions), 4)
        self.assertNotIn('path_length', transformed.columns)
        np.testing.assert_array_equal(selector.get_support(), original_support)
        np.testing.assert_array_equal(selector.variances_, original_variances)

    def test_fitted_pipeline_rejects_reordered_and_nonfinite_validation(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline()
        pipeline.fit(x_train, y_train)
        invalid_inputs = {'reordered': x_train.iloc[:3, ::-1].copy()}
        for value in (float('nan'), float('inf')):
            invalid = x_train.iloc[:3].copy()
            invalid.iloc[0, 0] = value
            invalid_inputs[str(value)] = invalid
        for case, invalid in invalid_inputs.items():
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    pipeline.predict(invalid)

    def test_saved_pipeline_roundtrip_preserves_predictions_and_contract(self):
        x_train, y_train = rows_to_xy(synthetic_rows())
        pipeline = make_pipeline().fit(x_train, y_train)
        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / 'pipeline.joblib'
            joblib.dump(pipeline, model_path)
            restored = joblib.load(model_path)
        np.testing.assert_array_equal(pipeline.predict(x_train), restored.predict(x_train))
        np.testing.assert_allclose(pipeline.predict_proba(x_train), restored.predict_proba(x_train))
        np.testing.assert_array_equal(pipeline.feature_names_in_, restored.feature_names_in_)
        np.testing.assert_array_equal(
            pipeline.named_steps['drop_constant'].get_support(),
            restored.named_steps['drop_constant'].get_support(),
        )


class MetricsTests(unittest.TestCase):
    def test_false_positive_rate_uses_actual_normal_count(self):
        # TN=3, FP=1, FN=1, TP=2. False alarm denominator is TN+FP=4,
        # not all seven records and not the three positive predictions.
        result = binary_metrics([0, 0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 0, 1, 1])
        self.assertEqual(result['confusion_matrix'], [[3, 1], [1, 2]])
        self.assertEqual([result[key] for key in ('tn', 'fp', 'fn', 'tp')], [3, 1, 1, 2])
        self.assertAlmostEqual(result['false_positive_rate'], 1 / 4)
        self.assertAlmostEqual(result['accuracy'], 5 / 7)
        self.assertAlmostEqual(result['precision'], 2 / 3)
        self.assertAlmostEqual(result['recall'], 2 / 3)
        self.assertAlmostEqual(result['f1'], 2 / 3)


class ExperimentBoundaryTests(unittest.TestCase):
    def test_experiment_never_reads_test_or_fits_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
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
                if split != 'test':
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

            original_open = Path.open

            def forbid_test_features(path, *args, **kwargs):
                if path.name == 'test_features.jsonl':
                    raise AssertionError('Held-out test features must not be opened')
                return original_open(path, *args, **kwargs)

            output_dir = project / 'new-model'
            with patch.object(Path, 'open', forbid_test_features):
                run = run_experiment(project, output_dir)
            self.assertFalse((split_dir / 'test_features.jsonl').exists())
            self.assertFalse(run['test_features_loaded'])
            self.assertFalse(run['test_evaluated'])
            self.assertEqual(run['training_records'], 24)
            self.assertEqual(run['validation_records'], 8)
            self.assertIn('path_length', run['dropped_constant_features'])
            self.assertEqual(run['train_constant_values']['path_length'], 7.0)
            restored = joblib.load(output_dir / 'pipeline.joblib')
            retained = restored.named_steps['drop_constant'].get_feature_names_out()
            self.assertNotIn('path_length', retained)
            for filename in ('pipeline.joblib', 'run.json', 'validation_predictions.jsonl',
                             'validation_errors.jsonl'):
                self.assertTrue((output_dir / filename).is_file())
            predictions = [json.loads(line) for line in
                           (output_dir / 'validation_predictions.jsonl').read_text().splitlines()]
            self.assertEqual(len(predictions), 8)
            self.assertTrue(all(row['sample_id'].startswith('validation:') for row in predictions))


if __name__ == '__main__':
    unittest.main()
