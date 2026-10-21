import copy
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import staging_retained_controls as c


class RetainedHostedControls(unittest.TestCase):
    def run_controls(self, root):
        return c.controls(root, time.monotonic() + 30)

    def test_five_real_traversal_controls_and_owned_cleanup(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            row = self.run_controls(root)
            self.assertEqual(c.validate_receipt(row), row)
            self.assertEqual([r['id'] for r in row['cases']], [case for case, _ in c.CASES])
            self.assertEqual(list(root.iterdir()), [])
            self.assertEqual(row['unread_mode'], 'injected_scandir_permission_error')

    def test_missing_native_link_is_inconclusive_not_skipped(self):
        with tempfile.TemporaryDirectory() as name, mock.patch.object(c, 'make_link', side_effect=c.q.Refused('retained_control_link_unavailable')):
            with self.assertRaisesRegex(c.q.Refused, 'retained_control_link_unavailable'):
                self.run_controls(Path(name).resolve())

    def test_wrong_refusal_or_silent_admission_fails(self):
        with tempfile.TemporaryDirectory() as name, mock.patch.object(c.m, 'retained_guard', return_value={'allowed_retained_file_count': 0}):
            with self.assertRaisesRegex(c.q.Refused, 'retained_control_outcome_mismatch'):
                self.run_controls(Path(name).resolve())

    def test_unexpected_refusal_code_does_not_satisfy_negative_control(self):
        with tempfile.TemporaryDirectory() as name, mock.patch.object(c.m, 'retained_guard', side_effect=c.q.Refused('wrong_refusal')):
            with self.assertRaisesRegex(c.q.Refused, 'retained_control_outcome_mismatch'):
                self.run_controls(Path(name).resolve())

    def test_unexpected_exception_is_not_expected_refusal(self):
        with tempfile.TemporaryDirectory() as name, mock.patch.object(c.m, 'retained_guard', side_effect=ValueError('synthetic')):
            with self.assertRaises(ValueError):
                self.run_controls(Path(name).resolve())

    def test_expired_common_deadline_stops_controls(self):
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaisesRegex(c.q.Refused, 'global_budget_exhausted'):
                c.controls(Path(name).resolve(), time.monotonic() - 1)

    def test_receipt_schema_count_order_types_and_refusals_are_exact(self):
        with tempfile.TemporaryDirectory() as name:
            row = self.run_controls(Path(name).resolve())
        variants = [{}, row | {'extra': True}, row | {'count': True}, row | {'passed': 1},
                    row | {'native_link_kind': 'unsupported'}, row | {'fixture_cleanup_verified': False}]
        for field, value in (('id', 'unknown'), ('refusal', None), ('passed', 1)):
            changed = copy.deepcopy(row)
            changed['cases'][1][field] = value
            variants.append(changed)
        for changed in variants:
            with self.assertRaises(c.q.Refused):
                c.validate_receipt(changed)


if __name__ == '__main__':
    unittest.main()
