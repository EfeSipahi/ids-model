"""Synthetic checks for classification metrics computed from saved predictions.

These tests never open the real experiment records.
"""
import json
import tempfile
import unittest
from pathlib import Path

from evaluate_predictions import evaluate_rows, run
from train_random_forest import binary_metrics


def prediction_rows(pairs):
    return [dict(sample_id=f'row:{index}', group_id=f'group:{index}', label=label,
                 prediction=int(score > 0.5), anomalous_score=score,
                 outcome=('TP' if label else 'FP') if score > 0.5 else ('FN' if label else 'TN'))
            for index, (label, score) in enumerate(pairs)]


# TN=2, FP=1, FN=1, TP=2. Two of the nine normal/anomalous score pairs are
# ranked the wrong way round (normal 0.7 above anomalous 0.3 and 0.6): AUC 7/9.
PAIRS = [(0, 0.1), (0, 0.2), (0, 0.7), (1, 0.3), (1, 0.6), (1, 0.9)]


class EvaluateRowsTests(unittest.TestCase):
    def test_all_classification_metrics_from_known_predictions(self):
        result = evaluate_rows(prediction_rows(PAIRS))
        metrics = result['metrics']
        self.assertEqual(result['records'], 6)
        self.assertEqual(result['labels'], {'0': 3, '1': 3})
        self.assertEqual(metrics['confusion_matrix'], [[2, 1], [1, 2]])
        self.assertEqual([metrics[key] for key in ('tn', 'fp', 'fn', 'tp')], [2, 1, 1, 2])
        for key in ('accuracy', 'precision', 'recall', 'f1'):
            self.assertAlmostEqual(metrics[key], 2 / 3)
        self.assertAlmostEqual(metrics['false_positive_rate'], 1 / 3)
        self.assertAlmostEqual(metrics['roc_auc'], 7 / 9)

    def test_roc_curve_runs_from_origin_to_top_right(self):
        curve = evaluate_rows(prediction_rows(PAIRS))['roc_curve']
        self.assertEqual(curve[0], dict(threshold=None, false_positive_rate=0.0, true_positive_rate=0.0))
        self.assertEqual((curve[-1]['false_positive_rate'], curve[-1]['true_positive_rate']), (1.0, 1.0))
        thresholds = [point['threshold'] for point in curve[1:]]
        self.assertEqual(thresholds, sorted(thresholds, reverse=True))
        json.dumps(curve, allow_nan=False)

    def test_inconsistent_records_are_rejected(self):
        def flip_prediction(rows):
            rows[0]['prediction'] = 1

        def wrong_outcome(rows):
            rows[0]['outcome'] = 'TP'

        def score_out_of_range(rows):
            rows[5]['anomalous_score'] = 1.5

        def single_class(rows):
            del rows[3:]

        for mutate in (flip_prediction, wrong_outcome, score_out_of_range, single_class):
            with self.subTest(mutate=mutate.__name__):
                rows = prediction_rows(PAIRS)
                mutate(rows)
                with self.assertRaises(ValueError):
                    evaluate_rows(rows)
        with self.assertRaises(ValueError):
            evaluate_rows([])

    def test_recorded_threshold_other_than_default_is_respected(self):
        # At 0.25 the anomalous 0.3 row is caught too: TN=2, FP=1, FN=0, TP=3.
        rows = prediction_rows(PAIRS)
        rows[3].update(prediction=1, outcome='TP')
        metrics = evaluate_rows(rows, threshold=0.25)['metrics']
        self.assertEqual([metrics[key] for key in ('tn', 'fp', 'fn', 'tp')], [2, 1, 0, 3])
        self.assertAlmostEqual(metrics['roc_auc'], 7 / 9)
        with self.assertRaises(ValueError):
            evaluate_rows(rows)

    def test_mismatch_with_recorded_metrics_is_rejected(self):
        rows = prediction_rows(PAIRS)
        recorded = binary_metrics([row['label'] for row in rows], [row['prediction'] for row in rows])
        evaluate_rows(rows, recorded)
        with self.assertRaises(ValueError):
            evaluate_rows(rows, dict(recorded, fp=recorded['fp'] + 1))


class RunTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.project = Path(directory.name)
        self.rows = prediction_rows(PAIRS)
        self.recorded = binary_metrics([row['label'] for row in self.rows],
                                       [row['prediction'] for row in self.rows])
        self.model_dir = self.project / 'models/demo-v1'
        self.model_dir.mkdir(parents=True)
        self.write_jsonl(self.model_dir / 'validation_predictions.jsonl', self.rows)
        (self.model_dir / 'run.json').write_text(json.dumps(dict(
            version='demo-v1', decision=dict(threshold=0.5),
            validation=dict(random_forest=self.recorded, dummy_most_frequent={}))), encoding='utf-8')

    @staticmethod
    def write_jsonl(path, rows):
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')

    def snapshot(self):
        return {str(path.relative_to(self.project)): path.read_bytes()
                for path in self.project.rglob('*') if path.is_file()}

    def test_validation_only_until_a_test_record_exists(self):
        before = self.snapshot()
        result = run(self.project, 'demo-v1')
        self.assertEqual(list(result['splits']), ['validation'])
        self.assertEqual(result['model'], 'random_forest')
        self.assertFalse(result['model_loaded'])
        output = self.project / 'reports/demo-v1-metrics/classification_metrics.json'
        self.assertEqual(json.loads(output.read_text(encoding='utf-8')), result)
        after = self.snapshot()
        del after['reports/demo-v1-metrics/classification_metrics.json']
        self.assertEqual(after, before)
        with self.assertRaises(FileExistsError):
            run(self.project, 'demo-v1')

    def test_recorded_test_predictions_are_included(self):
        test_dir = self.project / 'reports/demo-v1-test'
        test_dir.mkdir(parents=True)
        self.write_jsonl(test_dir / 'test_predictions.jsonl', self.rows)
        (test_dir / 'test_report.json').write_text(json.dumps(dict(metrics=self.recorded)), encoding='utf-8')
        result = run(self.project, 'demo-v1')
        self.assertEqual(list(result['splits']), ['validation', 'test'])
        self.assertAlmostEqual(result['splits']['test']['metrics']['roc_auc'], 7 / 9)
        self.assertEqual(set(result['source_sha256']), {
            'models/demo-v1/validation_predictions.jsonl', 'reports/demo-v1-test/test_predictions.jsonl'})

    def test_threshold_is_read_from_the_training_record(self):
        self.rows[3].update(prediction=1, outcome='TP')
        self.write_jsonl(self.model_dir / 'validation_predictions.jsonl', self.rows)
        recorded = binary_metrics([row['label'] for row in self.rows], [row['prediction'] for row in self.rows])
        run_path = self.model_dir / 'run.json'
        record = json.loads(run_path.read_text(encoding='utf-8'))
        record['validation']['random_forest'] = recorded
        run_path.write_text(json.dumps(record), encoding='utf-8')
        with self.assertRaises(ValueError):
            run(self.project, 'demo-v1')
        record['decision']['threshold'] = 0.25
        run_path.write_text(json.dumps(record), encoding='utf-8')
        result = run(self.project, 'demo-v1')
        self.assertEqual(result['threshold'], 0.25)
        self.assertEqual(result['splits']['validation']['metrics']['tp'], 3)

    def test_changed_predictions_do_not_produce_a_report(self):
        self.rows[2]['anomalous_score'] = 0.4
        self.rows[2]['prediction'], self.rows[2]['outcome'] = 0, 'TN'
        self.write_jsonl(self.model_dir / 'validation_predictions.jsonl', self.rows)
        with self.assertRaises(ValueError):
            run(self.project, 'demo-v1')
        self.assertFalse((self.project / 'reports/demo-v1-metrics').exists())


if __name__ == '__main__':
    unittest.main()
