"""Synthetic checks for the tuned (v2) training boundary.

These tests never open the real train, validation, or held-out test files.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np

from test_train_logistic_regression import build_synthetic_project
from test_train_random_forest import synthetic_rows
import train_tuned
from train_random_forest import read_jsonl, rows_to_xy
from train_tuned import MODELS, THRESHOLDS, decide, out_of_fold_scores, run_experiment, search

# Two cheap candidates per model keep the search fast; the real grids are checked separately.
SMALL_GRIDS = {
    'rf': [dict(random_state=42, n_jobs=1, n_estimators=10, max_depth=3, min_samples_leaf=2, max_features='sqrt'),
           dict(random_state=42, n_jobs=1, n_estimators=10, max_depth=None, min_samples_leaf=1, max_features=0.5)],
    'logreg': [dict(C=0.1, class_weight=None, max_iter=5000, l1_ratio=0.0, solver='lbfgs'),
               dict(C=1.0, class_weight='balanced', max_iter=5000, l1_ratio=1.0, solver='liblinear', random_state=42)],
}


class GridTests(unittest.TestCase):
    def test_real_grids_build_valid_pipelines_with_v1_preprocessing(self):
        self.assertEqual(len(MODELS['rf']['grid']), 64)
        self.assertEqual(len(MODELS['logreg']['grid']), 36)
        self.assertEqual(THRESHOLDS, (0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7))
        steps = {'rf': ['finite', 'drop_constant', 'forest'],
                 'logreg': ['finite', 'drop_constant', 'log1p', 'scale', 'logreg']}
        for model, spec in MODELS.items():
            self.assertEqual(len({json.dumps(params, sort_keys=True) for params in spec['grid']}), len(spec['grid']))
            for params in spec['grid']:
                pipeline = train_tuned.build_pipeline(spec, params)
                self.assertEqual(list(pipeline.named_steps), steps[model])
                actual = pipeline.named_steps[spec['step']].get_params()
                self.assertEqual({key: actual[key] for key in params}, params)


class CrossValidationTests(unittest.TestCase):
    def test_every_row_is_scored_once_and_groups_stay_in_one_fold(self):
        x, y = rows_to_xy(synthetic_rows(40))
        groups = np.asarray([f'group:{index // 4}' for index in range(40)])
        held_out = []
        real_scores = train_tuned.anomalous_scores

        def record(pipeline, held):
            held_out.append(list(held.index))
            return real_scores(pipeline, held)

        with patch.object(train_tuned, 'anomalous_scores', record):
            scores = out_of_fold_scores(MODELS['logreg'], SMALL_GRIDS['logreg'][0], x, y, groups)
        self.assertEqual(len(held_out), 5)
        self.assertEqual(sorted(index for fold in held_out for index in fold), list(range(40)))
        fold_groups = [set(groups[fold]) for fold in held_out]
        for first in range(5):
            for second in range(first + 1, 5):
                self.assertFalse(fold_groups[first] & fold_groups[second])
        self.assertTrue(((scores >= 0) & (scores <= 1)).all())


class SelectionRuleTests(unittest.TestCase):
    def select(self, y, candidate_scores):
        grid = [dict(candidate=index) for index in range(len(candidate_scores))]
        with patch.object(train_tuned, 'out_of_fold_scores',
                          side_effect=[np.asarray(scores, dtype=float) for scores in candidate_scores]):
            return search(MODELS['rf'], None, np.asarray(y), None, grid)

    def test_highest_f1_wins_and_threshold_ties_stay_near_default(self):
        # Candidate 1 misses one anomalous row at 0.5 (F1 0.8) but beats
        # candidate 0 (F1 2/3). Thresholds 0.30-0.40 all separate it perfectly.
        found = self.select([0, 0, 0, 1, 1, 1], [[0.1, 0.2, 0.6, 0.4, 0.8, 0.9],
                                                 [0.1, 0.2, 0.3, 0.45, 0.8, 0.9]])
        self.assertEqual(found['selected_index'], 1)
        self.assertEqual(found['selected_params'], dict(candidate=1))
        self.assertAlmostEqual(found['selected_cv_at_0_5']['f1'], 0.8)
        self.assertEqual(found['selected_threshold'], 0.4)
        self.assertEqual(found['selected_cv']['f1'], 1.0)
        self.assertEqual([row['threshold'] for row in found['threshold_search']], list(THRESHOLDS))
        self.assertEqual(len(found['candidates']), 2)

    def test_equal_f1_prefers_fewer_false_alarms_then_earlier_candidate(self):
        y = [0, 0, 0, 0, 1, 1, 1, 1]
        noisy = [0.1, 0.1, 0.9, 0.9, 0.1, 0.9, 0.9, 0.9]    # TP3 FN1 FP2: F1 2/3, FPR 0.5
        quiet = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.9, 0.9]    # TP2 FN2 FP0: F1 2/3, FPR 0
        self.assertEqual(self.select(y, [noisy, quiet])['selected_index'], 1)
        self.assertEqual(self.select(y, [quiet, noisy])['selected_index'], 0)
        self.assertEqual(self.select(y, [quiet, quiet])['selected_index'], 0)


class ExperimentBoundaryTests(unittest.TestCase):
    def run_in_new_project(self, model, change_validation=None):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        project = Path(directory.name)
        split_dir = build_synthetic_project(project)
        if change_validation:
            path = split_dir / 'validation_features.jsonl'
            rows = read_jsonl(path)
            change_validation(rows)
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
        original_open = Path.open

        def forbid_test_features(path, *args, **kwargs):
            if path.name == 'test_features.jsonl':
                raise AssertionError('Held-out test features must not be opened')
            return original_open(path, *args, **kwargs)

        output_dir = project / 'models' / MODELS[model]['version']
        with patch.object(Path, 'open', forbid_test_features):
            run = run_experiment(project, output_dir, model, SMALL_GRIDS[model])
        return project, split_dir, output_dir, run

    def test_outputs_are_consistent_with_recorded_selection(self):
        for model in MODELS:
            with self.subTest(model=model):
                project, split_dir, output_dir, run = self.run_in_new_project(model)
                spec = MODELS[model]
                self.assertEqual(run['version'], spec['version'])
                self.assertFalse(run['test_features_loaded'])
                self.assertFalse(run['test_evaluated'])
                self.assertEqual((run['training_records'], run['validation_records']), (24, 8))
                self.assertIn('path_length', run['dropped_constant_features'])
                self.assertIn(run['selection']['selected_params'], SMALL_GRIDS[model])
                self.assertEqual(run['selection']['candidates'], 2)
                threshold = run['decision']['threshold']
                self.assertIn(threshold, THRESHOLDS)
                self.assertTrue(run['decision']['threshold_tuned'])
                for filename in ('pipeline.joblib', 'run.json', 'search_results.json',
                                 'validation_predictions.jsonl', 'validation_errors.jsonl'):
                    self.assertTrue((output_dir / filename).is_file())
                self.assertEqual(json.loads((output_dir / 'run.json').read_text(encoding='utf-8')), run)
                searched = json.loads((output_dir / 'search_results.json').read_text(encoding='utf-8'))
                self.assertEqual([c['params'] for c in searched['candidates']], SMALL_GRIDS[model])

                restored = joblib.load(output_dir / 'pipeline.joblib')
                selected = run['selection']['selected_params']
                actual = restored.named_steps[spec['step']].get_params()
                self.assertEqual({key: actual[key] for key in selected}, selected)
                predictions = read_jsonl(output_dir / 'validation_predictions.jsonl')
                self.assertEqual(len(predictions), 8)
                self.assertTrue(all(row['sample_id'].startswith('validation:') for row in predictions))
                x_validation, y_validation = rows_to_xy(read_jsonl(split_dir / 'validation_features.jsonl'))
                scores = restored.predict_proba(x_validation)[:, 1]
                np.testing.assert_allclose(scores, [row['anomalous_score'] for row in predictions])
                # The recorded decisions follow the tuned threshold, not predict().
                np.testing.assert_array_equal(decide(scores, threshold), [row['prediction'] for row in predictions])
                metrics = run['validation'][spec['name']]
                self.assertEqual(metrics['tp'] + metrics['fn'], int(y_validation.sum()))
                with self.assertRaises(FileExistsError):
                    run_experiment(project, output_dir, model, SMALL_GRIDS[model])

    def test_validation_data_cannot_influence_the_selection(self):
        def distort(rows):
            for row in rows:
                for name in row['features']:
                    row['features'][name] = row['features'][name] * 37 + 5

        for model in MODELS:
            with self.subTest(model=model):
                *_, first_dir, first = self.run_in_new_project(model)
                *_, second_dir, second = self.run_in_new_project(model, distort)
                self.assertEqual(first['selection'], second['selection'])
                self.assertEqual(first['decision'], second['decision'])
                self.assertEqual(first['model_parameters'], second['model_parameters'])
                self.assertEqual((first_dir / 'search_results.json').read_bytes(),
                                 (second_dir / 'search_results.json').read_bytes())
                self.assertNotEqual((first_dir / 'validation_predictions.jsonl').read_bytes(),
                                    (second_dir / 'validation_predictions.jsonl').read_bytes())


if __name__ == '__main__':
    unittest.main()
