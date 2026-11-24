import copy
import unittest

from produkt.werkzeuge.steuerung import Invalid
from produkt.werkzeuge.steuerung.contracts import sha
from produkt.werkzeuge.steuerung.gates import JobRequirement, MANDATORY_JOBS, Policy, validate_report


def policy_data():
    return {"candidate_digest": sha(b"synthetic candidate"), "archive_digest": sha(b"synthetic archive"),
            "rules_digest": sha(b"fixed synthetic rules"), "issuer": "synthetic-verdict-issuer",
            "jobs": [{"name": name, "issuer": "synthetic-ci-issuer", "cases": index + 1}
                     for index, name in enumerate(sorted(MANDATORY_JOBS))]}


def report_data(policy):
    binding = {key: policy[key] for key in ("candidate_digest", "archive_digest", "rules_digest")}
    return {"schema_version": 1, "kind": "ci_attestation", "issuer": policy["issuer"],
            **binding, "status": "passed", "executed": True,
            "jobs": [{"name": row["name"], "issuer": row["issuer"], **binding,
                      "status": "passed", "executed": True, "expected_cases": row["cases"],
                      "executed_cases": row["cases"], "passed_cases": row["cases"]}
                     for row in policy["jobs"]]}


class GateTests(unittest.TestCase):
    def setUp(self):
        self.data = policy_data()
        self.policy = Policy.from_dict(self.data)
        self.report = report_data(self.data)

    def rejected(self, report):
        result = validate_report(report, self.policy)
        self.assertFalse(result.checks_valid)
        self.assertTrue(result.errors)
        self.assertFalse(result.release_authorized)

    def test_complete_structure_is_not_authenticated_release_evidence(self):
        result = validate_report(self.report, self.policy)
        self.assertTrue(result.checks_valid)
        self.assertFalse(result.release_authorized)
        self.assertEqual(result.authentication, "not_verified")

    def test_local_simulation_is_not_a_real_release_attestation(self):
        self.report["kind"] = "local_simulation"
        self.rejected(self.report)

    def test_missing_required_top_level_fields_fail_closed(self):
        for field in self.report:
            report = copy.deepcopy(self.report)
            del report[field]
            with self.subTest(field=field):
                self.rejected(report)

    def test_each_mandatory_job_must_be_present_exactly_once(self):
        for index in range(len(self.report["jobs"])):
            report = copy.deepcopy(self.report)
            del report["jobs"][index]
            with self.subTest(index=index):
                self.rejected(report)
        for rows in ([], self.report["jobs"] + [self.report["jobs"][0]]):
            self.rejected({**self.report, "jobs": rows})

    def test_every_job_requires_passed_and_boolean_executed_true(self):
        for index in range(len(self.report["jobs"])):
            for key, value in (("status", "skipped"), ("status", "failed"), ("status", "open"),
                               ("executed", False), ("executed", 1), ("executed", "true")):
                report = copy.deepcopy(self.report)
                report["jobs"][index][key] = value
                with self.subTest(index=index, key=key, value=value):
                    self.rejected(report)

    def test_positive_exact_expected_executed_and_passed_counts(self):
        for key in ("expected_cases", "executed_cases", "passed_cases"):
            for value in (0, -1, True, 1.0, "1", None, 999):
                report = copy.deepcopy(self.report)
                report["jobs"][0][key] = value
                with self.subTest(key=key, value=value):
                    self.rejected(report)
        report = copy.deepcopy(self.report)
        del report["jobs"][0]["executed_cases"]
        self.rejected(report)

    def test_exact_candidate_archive_rules_and_issuer_at_both_levels(self):
        for index in (None, *range(len(self.report["jobs"]))):
            for key in ("candidate_digest", "archive_digest", "rules_digest", "issuer"):
                report = copy.deepcopy(self.report)
                target = report if index is None else report["jobs"][index]
                target[key] = "wrong-issuer" if key == "issuer" else sha(b"other binding")
                with self.subTest(index=index, key=key):
                    self.rejected(report)

    def test_digest_format_is_not_normalized(self):
        for value in (None, "", "a" * 40, "A" * 64, "a" * 64 + " ", ["a" * 64]):
            with self.subTest(value=value):
                self.rejected({**self.report, "archive_digest": value})

    def test_policy_cannot_omit_jobs_or_accept_zero_or_boolean_counts(self):
        for jobs in ([], self.data["jobs"][:-1], self.data["jobs"] + [self.data["jobs"][0]]):
            with self.subTest(jobs=jobs), self.assertRaises(Invalid):
                Policy.from_dict({**self.data, "jobs": jobs})
        for count in (0, -1, True, 1.0):
            data = copy.deepcopy(self.data)
            data["jobs"][0]["cases"] = count
            with self.subTest(count=count), self.assertRaises(Invalid):
                Policy.from_dict(data)

    def test_policy_requires_explicit_valid_digests_and_expected_issuers(self):
        for key in ("candidate_digest", "archive_digest", "rules_digest", "issuer"):
            data = copy.deepcopy(self.data)
            del data[key]
            with self.subTest(key=key), self.assertRaises(Invalid):
                Policy.from_dict(data)
        with self.assertRaises(Invalid):
            validate_report(self.report, None)
        with self.assertRaises(Invalid):
            Policy.from_dict({**self.data, "issuer": " "})

    def test_failed_older_candidate_cannot_be_relabelled_by_new_policy(self):
        old_report = copy.deepcopy(self.report)
        old_report["jobs"][0]["status"] = "failed"
        new_data = {**self.data, "candidate_digest": sha(b"next synthetic candidate")}
        result = validate_report(old_report, Policy.from_dict(new_data))
        self.assertFalse(result.checks_valid)
        self.assertGreaterEqual(len(result.errors), 2)

    def test_malformed_policy_names_and_issuers_raise_controlled_error(self):
        for field, value in (("name", []), ("name", {}), ("name", ""),
                             ("issuer", None), ("issuer", " ")):
            data = copy.deepcopy(self.data)
            data["jobs"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(Invalid):
                Policy.from_dict(data)

    def test_each_job_field_is_mandatory_and_unknown_fields_fail(self):
        for field in self.report["jobs"][0]:
            report = copy.deepcopy(self.report)
            del report["jobs"][0][field]
            with self.subTest(field=field):
                self.rejected(report)
        report = copy.deepcopy(self.report)
        report["jobs"][0]["allow_skip"] = True
        self.rejected(report)

    def test_malformed_or_unknown_report_shape_fails_closed(self):
        for report in (None, [], {}, {**self.report, "unexpected": True},
                       {**self.report, "schema_version": True}, {**self.report, "jobs": {}}):
            with self.subTest(report=report):
                self.rejected(report)
