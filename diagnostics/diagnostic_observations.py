"""Diagnostic-local observations. These never grant admission or repair a failure."""
import json
import unittest

import measure_lazy_suite_ids as q
from parallel_reader_capture import summary_counts, FAILED, OK

PAIR_COMMANDS = ('phi_layers', 'suite', 'publication_measurements', 'threshold_sheet', 'phi_shape_only')
PHASES = frozenset(('preflight', 'source', 'native', 'retained', 'contract', 'snapshot', 'clone',
    'temp', 'initial_guard', 'discovery', 'discovery_validate', 'discovery_guard',
    'final_source', 'environment', 'cleanup', 'pair_behavior', 'pair_explicit') + tuple(
        prefix + name for prefix in ('pair_', 'pair_guard_') for name in PAIR_COMMANDS) + tuple(
        prefix + str(index) for prefix in ('case_', 'case_verify_', 'case_guard_') for index in range(3)))
CHILD_PHASES = frozenset(('native', 'retained', 'contract', 'snapshot', 'temp', 'discovery', 'case_0', 'case_1', 'case_2'))
EXCEPTIONS = (AssertionError, ValueError, TypeError, KeyError, OSError, PermissionError,
              FileNotFoundError, TimeoutError, RuntimeError, KeyboardInterrupt, SystemExit, q.Refused)
PREFIX = 'DIAGNOSTIC_CONTROL_OBSERVATION:'
REASONS = frozenset(('unit_discovery_identity_changed', 'matched_worker_topology_changed', 'suite_accounting_incomplete', 'estimated_maintainer_plan_no_longer_fits', 'matched_environment_or_discovery_changed', 'windows_python_pin_required', 'unauthorized_event_or_rerun', 'snapshot_fixture_scope_invalid', 'snapshot_population_changed', 'snapshot_fixture_cleanup_failed', 'generated_file_creation_changed', 'generated_native_snapshot_unstable',
    'generated_handle_cleanup_failed', 'generated_native_abi_unavailable', 'generated_native_path_kind_unsupported', 'global_budget_exhausted', 'disk_reserve_exhausted', 'capture_limit_exceeded',
    'capture_or_disk_reserve_exhausted', 'process_cleanup_unverified', 'probe_failed_or_unread',
    'owner_controls_failed', 'retained_controls_failed', 'retained_controls_receipt_invalid',
    'retained_controls_native_link_missing', 'unit_discovery_receipt_invalid',
    'generated_file_identity_changed', 'generated_file_unread', 'generated_file_unsafe',
    'generated_handle_metadata_unread', 'generated_output_unexpected', 'observer_not_clean',
    'seed_not_clean', 'source_inventory_changed', 'environment_changed',
    'retained_control_outcome_mismatch', 'retained_control_link_unavailable',
    'retained_control_link_cleanup_failed', 'retained_control_link_target_changed',
    'retained_control_cleanup_failed'))


# Source-known full-pair refusal codes only; never derive categories from payloads.
REASONS = REASONS | frozenset(('baseline_module_hash_changed', 'baseline_not_safe_or_passed', 'baseline_receipt_missing_or_large', 'checkout_overlap', 'clone_failed', 'controls_population_changed', 'cpu_identity_unread', 'discovery_identity_invalid', 'environment_changed', 'estimated_maintainer_plan_no_longer_fits', 'global_budget_exhausted', 'initial_clone_inventory_changed', 'initial_suite_weights_or_scratch_present', 'matched_environment_or_discovery_changed', 'matched_worker_topology_changed', 'observer_branch_scope_changed', 'observer_source_changed', 'owner_controls_failed', 'pair_receipt_limit', 'precommand_identity_limit', 'prepared_clone_inventory_changed', 'retained_output_limit', 'runner_identity_unread', 'seed_changed', 'setup_estimate_exhausted', 'source_history_shallow', 'source_hook_refuses_checkout_location', 'source_ref_unread', 'source_refs_changed', 'source_remote_head_changed', 'suite_accounting_incomplete', 'temp_inside_checkout', 'temp_validation_incomplete', 'unauthorized_event_or_rerun', 'unit_discovery_identity_changed', 'windows_python_pin_required', 'workflow_workspace_identity_changed', 'workflow_workspace_unavailable', 'workspace_ancestor_unsafe', 'workspace_clone_not_fresh', 'workspace_clone_not_shorter', 'workspace_clone_overlap', 'workspace_parent_inside_temp', 'workspace_path_noncanonical', 'workspace_source_path_too_long'))

# Fixed source/contract helper refusals invoked by the pair.
REASONS = REASONS | frozenset(('arguments_missing', 'baseline_module_hash_changed', 'budget_contract_changed', 'capture_limit_exceeded', 'capture_or_disk_reserve_exhausted', 'checkout_overlap', 'child_repo_missing', 'clone_failed', 'clone_root_ancestor_unsafe', 'clone_root_boundary_invalid', 'clone_root_not_shorter', 'controls_exit_mismatch', 'controls_population_changed', 'controls_rows_incomplete', 'controls_unexpected_outcome', 'controls_work_incomplete', 'discovery_population_changed', 'disk_reserve_exhausted', 'environment_changed', 'estimated_complete_plan_no_longer_fits', 'first_status_not_clean', 'generated_handle_cleanup_failed', 'git_unavailable', 'git_verification_failed', 'global_budget_exhausted', 'independent_clone_required', 'initial_clone_inventory_changed', 'measured_head_changed', 'measured_index_changed', 'measured_scope_changed', 'observer_branch_scope_changed', 'observer_dirty_at_finish', 'observer_source_changed', 'owner_control_rows_incomplete', 'owner_controls_failed', 'owner_controls_incomplete', 'prepared_clone_inventory_changed', 'private_roots_present', 'probe_failed_or_unread', 'process_cleanup_unverified', 'remaining_estimated_samples_do_not_fit', 'reviewed_raw_bytes_changed', 'seed_changed', 'setup_estimate_exhausted', 'shared_git_directory', 'shared_objects_refused', 'temp_inside_checkout', 'temp_validation_incomplete', 'timed_probe_incomplete_or_failed', 'tracked_raw_bytes_changed', 'tracked_reparse_path_changed', 'unauthorized_event_or_rerun', 'unknown_clone_role', 'unknown_control_variant', 'untracked_source_changed', 'windows_python_pin_required', 'wrong_source_head'))

# Fixed native contract need/refuse categories.
REASONS = REASONS | frozenset(('generated_comparison_stage_invalid', 'generated_date_interval_invalid', 'generated_directory_identity_changed', 'generated_directory_unread', 'generated_directory_unsafe', 'generated_discrepancy_limit', 'generated_entry_identity_changed', 'generated_entry_limit', 'generated_file_creation_changed', 'generated_file_identity_changed', 'generated_file_oversize', 'generated_file_unread', 'generated_file_unsafe', 'generated_handle_cleanup_failed', 'generated_handle_metadata_unread', 'generated_json_duplicate_key', 'generated_json_invalid', 'generated_marker_bytes_invalid', 'generated_marker_date_invalid', 'generated_marker_schema_invalid', 'generated_metadata_unread', 'generated_native_abi_unavailable', 'generated_native_path_kind_unsupported', 'generated_native_snapshot_unstable', 'generated_nofollow_unavailable', 'generated_output_discrepancies_found', 'generated_relative_path_invalid', 'generated_root_invalid', 'generated_state_invalid', 'generated_units_invalid', 'generated_weights_bytes_invalid', 'generated_weights_units_invalid', 'generated_weights_values_invalid', 'global_budget_exhausted'))


def reason_category(error):
    value = error.args[0] if type(error) is q.Refused and len(error.args) == 1 else None
    return value if type(value) is str and value in REASONS else 'unavailable'


def exception_category(error):
    return type(error).__name__ if type(error) in EXCEPTIONS else 'OtherException'


def phase_name(phase):
    return phase if type(phase) is str and phase in PHASES else 'unavailable'


def exit_state(value):
    return ('zero' if value == 0 else 'nonzero') if type(value) is int else 'unavailable'


def unique_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def metadata_flags(row):
    """Accept finite flags only; discard tokens and every raw metadata value."""
    from generated_output_contract import METADATA_FIELDS
    if type(row) is not dict:
        return None
    if row.get('stage') == 'read_length' and row.get('length_equal') is False:
        return {'stage': 'read_length', 'length_equal': False}
    if row.get('stage') not in ('before_open', 'before_after', 'after_final'):
        return None
    fields = row.get('fields_equal')
    if type(fields) is not dict or set(fields) != set(METADATA_FIELDS) or not all(type(v) is bool for v in fields.values()):
        return None
    birth = [row.get(key) for key in ('left_ctime_equals_birthtime', 'right_ctime_equals_birthtime')]
    if not all(type(v) is bool or v == 'unavailable' for v in birth):
        return None
    return {'stage': row['stage'], 'fields_equal': fields,
            'left_ctime_equals_birthtime': birth[0], 'right_ctime_equals_birthtime': birth[1]}


def contract_ids():
    from test_generated_output_contract import GeneratedOutputControls
    return tuple('test_generated_output_contract.GeneratedOutputControls.' + name
                 for name in GeneratedOutputControls.__dict__ if name.startswith('test_'))


def contract_child():
    """Same unittest population, with finite failure-only observations after mocks stop."""
    return control_child(('test_generated_output_contract',), contract_ids(), 41)


def control_child(modules, allowed, count):
    events = []
    class Result(unittest.TextTestResult):
        def record(self, test, err):
            identity = test.id()
            flags = []
            emitter = getattr(test, 'emit', None)
            for call in getattr(emitter, 'call_args_list', ()):
                if call.args == ('generated_file_comparison',):
                    row = metadata_flags(call.kwargs)
                    if row is not None and len(flags) < 8:
                        flags.append(row)
            if len(events) < count:
                events.append({'test_id': identity if identity in allowed else 'unknown',
                               'exception_category': exception_category(err[1]), 'metadata': flags})
        def addFailure(self, test, err):
            self.record(test, err)
            super().addFailure(test, err)
        def addError(self, test, err):
            self.record(test, err)
            super().addError(test, err)
        def addSubTest(self, test, subtest, err):
            if err is not None:
                self.record(test, err)
            super().addSubTest(test, subtest, err)
    class Runner(unittest.TextTestRunner):
        resultclass = Result
    program = unittest.TestProgram(module=None, argv=['unittest', *modules],
                                   testRunner=Runner, exit=False)
    result = program.result
    print(PREFIX + json.dumps({'events': events}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


def observe_result(phase, result, allowed_ids=()):
    bound = 73 if phase == 'snapshot' else 41 if phase == 'contract' else 9 if phase == 'native' else 5 if phase == 'retained' else 1
    row = {'phase': phase_name(phase), 'exit_state': exit_state(result.get('returncode')),
           'expected_test_count': 73 if phase == 'snapshot' else 41 if phase == 'contract' else 1 if phase in ('case_0', 'case_1', 'case_2') else None,
           'summary_read': False, 'tests_run': None, 'failures': None, 'errors': None,
           'skipped': None, 'failed_test_ids': [], 'unknown_failure_ids': 0,
           'unknown_failure_ids_truncated': False, 'counts_state': 'unread'}
    try:
        parsed = q.analyze_capture(result['stdout_path'], result['stderr_path'], result['returncode'], q.LOOKUPS[0])
        summaries = []
        for line in (result.get('stdout', '') + '\n' + result.get('stderr', '')).splitlines():
            match = FAILED.fullmatch(line) or OK.fullmatch(line)
            if match:
                summaries.append(summary_counts(match.group(1), successful=line.startswith('OK')))
        if parsed['structured_result_read'] and len(summaries) == 1 and not summaries[0].get('unread'):
            counts = {target: parsed[source] for target, source in
                (('tests_run', 'test_count'), ('failures', 'failures'), ('errors', 'errors'), ('skipped', 'skipped'))}
            row['summary_read'] = True
            if all(type(value) is int and 0 <= value <= bound for value in counts.values()):
                row.update(counts, counts_state='within_bound')
            else:
                row['counts_state'] = 'out_of_range'
        # Exact complete stock headers only, never subtest parameters or raw lines.
        for line in result.get('stderr', '').splitlines():
            if line.startswith(('FAIL: ', 'ERROR: ')):
                known = [identity for identity in allowed_ids if line ==
                         line.split(':', 1)[0] + ': ' + identity.rsplit('.', 1)[-1] + ' (' + identity + ')']
                if len(known) == 1:
                    if known[0] not in row['failed_test_ids']:
                        row['failed_test_ids'].append(known[0])
                else:
                    if row['unknown_failure_ids'] < bound:
                        row['unknown_failure_ids'] += 1
                    else:
                        row['unknown_failure_ids_truncated'] = True
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        row['capture_analysis'] = 'unread'
    q.emit('diagnostic_child_observed', **row)
    # Native JSON has private source frames: copy only finite categories/codes.
    try:
        if phase == 'native':
            from windows_job_probe_controls import PUBLIC_DIAGNOSTIC_CODES, DECLARED_CONTROL_IDS
            data = unique_json(result['stdout'])
            codes = data.get('diagnostic_codes', [])
            reported = data.get('status')
            passed_ids = data.get('passed_control_ids')
            error = data.get('error_type')
            q.emit('diagnostic_native_observed', reported_status=reported if reported in ('passed', 'failed') else 'unavailable',
                   exception_category=error if error in tuple(t.__name__ for t in EXCEPTIONS) + ('ProbeError',) else 'unavailable',
                   passed_control_ids=[value for value in passed_ids[:9] if value in DECLARED_CONTROL_IDS]
                   if type(passed_ids) is list else None,
                   diagnostic_codes=[code for code in codes[:32] if type(code) is str and code in PUBLIC_DIAGNOSTIC_CODES]
                   if type(codes) is list else [], receipt_object=type(data) is dict)
            detail = data.get('control_observation')
            if type(detail) is dict:
                current = detail.get('active_control_id')
                completed = detail.get('completed_control_ids')
                cleanup = detail.get('cleanup_state')
                primary = detail.get('primary_error_type')
                primary_codes = detail.get('primary_diagnostic_codes')
                q.emit('diagnostic_native_progress', active_control_id=current if current in DECLARED_CONTROL_IDS else None,
                       completed_control_ids=[value for value in completed[:9] if value in DECLARED_CONTROL_IDS]
                       if type(completed) is list else None,
                       cleanup_state=cleanup if cleanup in ('not_started', 'started', 'passed', 'failed') else 'unavailable',
                       primary_error_type=primary if primary in tuple(t.__name__ for t in EXCEPTIONS) + ('ProbeError',) else 'unavailable',
                       primary_diagnostic_codes=[value for value in primary_codes[:32] if type(value) is str and value in PUBLIC_DIAGNOSTIC_CODES]
                       if type(primary_codes) is list else None)
        elif phase == 'retained':
            from staging_retained_controls import CASES
            allowed = {case for case, _ in CASES} | {'fixture'}
            states = ('started', 'passed', 'cleanup_started', 'cleanup_passed', 'cleanup_failed', 'failed')
            for line in result.get('stderr', '').splitlines()[:64]:
                prefix = 'RETAINED_CONTROL_OBSERVATION:'
                if line.startswith(prefix):
                    data = unique_json(line[len(prefix):])
                    if type(data) is not dict or type(data.get('case')) is not str or data.get('case') not in allowed or data.get('state') not in states:
                        raise ValueError('invalid retained observation')
                    q.emit('diagnostic_retained_observed', case=data['case'], state=data['state'],
                           failure_stage=data.get('failure_stage') if data.get('failure_stage') in states else None,
                           exception_category=data.get('exception_category') if data.get('exception_category') in tuple(t.__name__ for t in EXCEPTIONS) else None,
                           reason=data.get('reason') if type(data.get('reason')) is str and data.get('reason') in REASONS else None)
        elif phase in ('contract', 'snapshot'):
            lines = [line[len(PREFIX):] for line in result['stdout'].splitlines() if line.startswith(PREFIX)]
            if len(lines) != 1:
                raise ValueError('missing or duplicate observation')
            data = unique_json(lines[0])
            if type(data) is not dict or type(data.get('events')) is not list or len(data['events']) > bound:
                raise ValueError('invalid observation')
            preflight = data.get('preflight_failure')
            if type(preflight) is dict:
                category, reason = preflight.get('exception_category'), preflight.get('reason')
                q.emit('diagnostic_control_preflight', phase=phase_name(phase),
                       exception_category=category if category in tuple(t.__name__ for t in EXCEPTIONS) else 'OtherException',
                       reason=reason if type(reason) is str and reason in REASONS else 'unavailable')
            for event in data['events']:
                if type(event) is not dict:
                    raise ValueError('invalid event')
                identity = event.get('test_id')
                category = event.get('exception_category')
                values = event.get('metadata')
                q.emit('diagnostic_contract_failure', test_id=identity if identity in allowed_ids else 'unknown',
                       exception_category=category if category in tuple(t.__name__ for t in EXCEPTIONS) else 'OtherException',
                       metadata_scope='observed_during_failed_test_not_causal_proof',
                       metadata=[safe for value in values[:8] if (safe := metadata_flags(value)) is not None]
                       if type(values) is list else [])
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
        q.emit('diagnostic_receipt_observed', phase=phase_name(phase), receipt_state='unread')
    return row


class ObservedSession(q.Session):
    phase = 'preflight'

    def run(self, argv, cwd):
        previous = len(getattr(self, 'owners', ()))
        try:
            result = super().run(argv, cwd)
        except BaseException as error:
            try:
                owners = getattr(self, 'owners', ())
                code = None
                if len(owners) > previous:
                    finished = owners[-1].result
                    if finished is not None:
                        code = finished.snapshot.root_exit_code
                q.emit('diagnostic_command_failed', phase=phase_name(self.phase),
                       exception_category=exception_category(error), reason=reason_category(error), exit_state=exit_state(code))
            except BaseException:
                pass  # A reporting failure must never replace the original command failure.
            raise
        if self.phase in CHILD_PHASES:
            try:
                allowed = contract_ids() if self.phase == 'contract' else ()
                if self.phase == 'snapshot':
                    from diagnose_windows_snapshot import control_groups
                    allowed = sum(control_groups().values(), ())
                if self.phase in ('case_0', 'case_1', 'case_2'):
                    from diagnose_generated_outputs import CASES
                    allowed = (CASES[int(self.phase[-1])],)
                observe_result(self.phase, result, allowed)
            except BaseException:
                try:
                    q.emit('diagnostic_receipt_observed', phase=phase_name(self.phase), receipt_state='unread')
                except BaseException:
                    pass
        return result
