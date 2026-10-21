#!/usr/bin/env python3
"""Unit tests for validate.py: every check, on a valid case and on cases built to
break it. Run:  python3 conformance-tests/harness/tools/test_validate.py
"""
import copy, hashlib, json, math, pathlib, shutil, sys, tempfile, unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import validate as v  # noqa: E402

HERE = v.HERE
EX = HERE / "examples"
INV = v.load_inventory()
REPORT = json.loads((EX / "cts-report--algebra.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((EX / "evidence-manifest--algebra.json").read_text(encoding="utf-8"))
EVIDENCE = EX / "evidence"


def report():
    return copy.deepcopy(REPORT)


def errors(r, manifest=MANIFEST, root=EVIDENCE):
    return v.check_report(r, INV, manifest, root)


def case(r, cid):
    return next(c for c in r["cases"] if c["case_id"] == cid)


def req(r, rid):
    return next(q for q in r["requirements"] if q["requirement_id"] == rid)


def resummarize(r):
    cnt = lambda items, key, keys: {k: sum(1 for i in items if i[key] == k) for k in keys}
    r["summary"] = {"cases": cnt(r["cases"], "outcome", v.ORDER),
                    "tests": cnt(r["tests"], "outcome", v.ORDER),
                    "requirements": cnt(r["requirements"], "state", v.STATES)}
    return r


class Algebra(unittest.TestCase):
    def test_test_summary_truth_table(self):
        T = v.summarize
        self.assertEqual(T(["PASS", "NOT_RUN", "NOT_APPLICABLE"]), "NOT_RUN")
        self.assertEqual(T(["PASS", "FAIL", "NOT_RUN"]), "FAIL")
        self.assertEqual(T(["PASS", "NOT_APPLICABLE"]), "PASS")
        self.assertEqual(T(["NOT_APPLICABLE"]), "NOT_APPLICABLE")

    def test_requirement_truth_table(self):
        S = v.requirement_state
        self.assertEqual(S(["a", "b"], {"a": "PASS", "b": "PASS"}), "verified")
        self.assertEqual(S(["a", "b"], {"a": "PASS", "b": "NOT_RUN"}), "unverified")
        self.assertEqual(S(["a", "b"], {"a": "PASS"}), "unverified")          # b not run
        self.assertEqual(S(["a", "b"], {"a": "PASS", "b": "NOT_APPLICABLE"}), "verified")
        self.assertEqual(S(["a", "b"], {"a": "NOT_RUN", "b": "FAIL"}), "violated")
        self.assertEqual(S(["a"], {"a": "NOT_APPLICABLE"}), "not_applicable")


class ReportValid(unittest.TestCase):
    def test_example_verifies(self):
        self.assertEqual(errors(report()), [])

    def test_edge_cases_present_in_example(self):
        r = report()
        cfg = next(t for t in r["tests"] if t["test_id"] == "CT-CFG-025")
        self.assertEqual(cfg["outcome"], "NOT_RUN")                        # PASS + NOT_RUN
        self.assertEqual(req(r, "R-0132")["state"], "not_applicable")      # only case unclaimed
        self.assertEqual(req(r, "R-0021")["state"], "unverified")          # CT-ASM-002 not planned
        self.assertEqual(req(r, "R-0361")["derived_from"], "R-0316")       # Restates
        self.assertEqual(len(r["requirements"]), len(INV["requirements"]))


class ReportInvalid(unittest.TestCase):
    def assertRejected(self, r, needle, manifest=MANIFEST, root=EVIDENCE):
        errs = errors(r, manifest, root)
        self.assertTrue(any(needle in e for e in errs), f"wanted {needle!r}, got {errs[:4]}")

    def test_duplicate_case(self):
        r = report(); r["cases"].append(copy.deepcopy(r["cases"][0]))
        self.assertRejected(r, "reported more than once")

    def test_missing_planned_case(self):
        r = report(); r["cases"] = [c for c in r["cases"] if c["case_id"] != "CT-CFG-025.05"]
        self.assertRejected(r, "cases reported differ from plan")

    def test_unplanned_case(self):
        r = report(); extra = copy.deepcopy(case(r, "CT-ASM-001"))
        extra["case_id"] = extra["test_id"] = "CT-ASM-002"; r["cases"].append(extra)
        self.assertRejected(r, "cases reported differ from plan")

    def test_test_missing_from_report(self):
        r = report(); r["tests"] = [t for t in r["tests"] if t["test_id"] != "CT-ASM-001"]
        self.assertRejected(r, "tests reported differ from plan")

    def test_test_outcome_hides_not_run(self):
        r = report(); next(t for t in r["tests"] if t["test_id"] == "CT-CFG-025")["outcome"] = "PASS"
        self.assertRejected(r, "its cases give NOT_RUN")

    def test_test_case_ids_differ(self):
        r = report(); t = next(t for t in r["tests"] if t["test_id"] == "CT-CFG-025")
        t["case_ids"] = t["case_ids"][:3]
        self.assertRejected(r, "case_ids differ from the CTS")

    def test_case_in_wrong_test(self):
        r = report(); case(r, "CT-ASM-001")["test_id"] = "CT-REL-023"
        self.assertRejected(r, "the CTS puts it in")

    def test_full_plan_that_is_not_full(self):
        r = report(); r["plan"]["scope"] = "full"
        self.assertRejected(r, "plan is full")

    def test_plan_names_unknown_test(self):
        r = report(); r["plan"]["test_ids"].append("CT-XYZ-999")
        self.assertRejected(r, "not in the CTS")

    def test_missing_requirement(self):
        r = report(); r["requirements"] = r["requirements"][1:]
        self.assertRejected(r, "requirements differ from Section 90")

    def test_duplicate_requirement(self):
        r = report(); r["requirements"].append(copy.deepcopy(r["requirements"][0]))
        self.assertRejected(r, "reported more than once")

    def test_wrong_trace(self):
        r = report(); req(r, "R-0021")["traced_to"] = ["CT-ASM-001"]
        self.assertRejected(r, "traced_to differs")

    def test_wrong_derived_from(self):
        r = report(); req(r, "R-0361").pop("derived_from")
        self.assertRejected(r, "derived_from differs")

    def test_requirement_state_overclaimed(self):
        r = report(); req(r, "R-0021")["state"] = "verified"; resummarize(r)
        self.assertRejected(r, "the algebra gives unverified")

    def test_summary_mismatch(self):
        r = report(); r["summary"]["requirements"]["verified"] += 1
        self.assertRejected(r, "summary.requirements")

    def test_capability_mismatch(self):
        r = report(); case(r, "CT-CFG-025.25")["capability"] = "core"
        self.assertRejected(r, "the CTS gives")

    def test_not_claimed_but_claimed(self):
        r = report(); r["provenance"]["capabilities_claimed"].append("seeded_controls")
        self.assertRejected(r, "but its capability is claimed")

    def test_unclaimed_capability_must_be_not_applicable(self):
        r = report(); r["provenance"]["capabilities_claimed"] = []
        self.assertRejected(r, "outcome must be NOT_APPLICABLE")

    def test_other_cts_revision(self):
        r = report(); r["provenance"]["cts_revision"] = "WD6"
        self.assertRejected(r, "the CTS here is")

    def test_evidence_not_in_manifest(self):
        r = report(); case(r, "CT-ASM-001")["evidence_refs"] = ["evidence://nowhere.json"]
        self.assertRejected(r, "not in the manifest")

    def test_review_missing(self):
        r = report(); r["manual_reviews"] = []
        self.assertRejected(r, "which the report lacks")

    def test_pass_without_evidence(self):
        r = report(); case(r, "CT-ASM-001")["evidence_refs"] = []
        self.assertRejected(r, "should be non-empty")

    def test_manifest_digest_not_the_reports(self):
        r = report(); r["evidence_manifest_sha256"] = "0" * 64
        self.assertRejected(r, "does not match the manifest")


class Evidence(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        shutil.copytree(EVIDENCE, self.tmp / "evidence")
        self.root = self.tmp / "evidence"
        self.m = copy.deepcopy(MANIFEST)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rehash(self):
        self.m.pop("manifest_sha256")
        self.m["manifest_sha256"] = hashlib.sha256(v.jcs(self.m).encode()).hexdigest()

    def errs(self):
        return v.check_manifest(self.m, self.root)

    def test_untouched_verifies(self):
        self.assertEqual(self.errs(), [])

    def test_one_byte_changed(self):
        p = self.root / "CT-SDK-001.json"; b = bytearray(p.read_bytes()); b[0] ^= 1
        p.write_bytes(bytes(b))
        self.assertTrue(any("does not match its digest" in e for e in self.errs()))

    def test_raw_object_removed(self):
        (self.root / "CT-SDK-001.json").unlink()
        self.assertTrue(any("is missing" in e for e in self.errs()))

    def test_redacted_copy_changed(self):
        p = self.root / "CT-ASM-001.redacted.json"; p.write_bytes(p.read_bytes() + b" ")
        self.assertTrue(any("redacted object" in e for e in self.errs()))

    def test_size_misstated(self):
        self.m["entries"][0]["raw_size"] += 1; self.rehash()
        self.assertTrue(any("bytes, the manifest says" in e for e in self.errs()))

    def test_manifest_edited_without_rehash(self):
        self.m["entries"][0]["collected_at"] = "2026-10-21T00:00:00Z"
        self.assertTrue(any("does not verify" in e for e in self.errs()))

    def test_duplicate_entry(self):
        self.m["entries"].append(copy.deepcopy(self.m["entries"][0])); self.rehash()
        self.assertTrue(any("more than once" in e for e in self.errs()))

    def test_reference_outside_root(self):
        self.m["entries"][0]["raw_ref"] = "evidence://../../etc/passwd"; self.rehash()
        self.assertTrue(any("outside the evidence root" in e for e in self.errs()))

    def test_report_fails_closed_on_missing_evidence(self):
        (self.root / "CT-SDK-001.json").unlink()
        self.assertTrue(any("is missing" in e for e in v.check_report(report(), INV, self.m, self.root)))


class Canonicalization(unittest.TestCase):
    def test_rfc_vectors(self):
        self.assertEqual(v.jcs_self_test(), [])

    def test_utf16_order_differs_from_code_point_order(self):
        doc = {"": 1, "\U0001f600": 2}
        self.assertNotEqual(v.jcs(doc), json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                                   ensure_ascii=False))

    def test_large_integer_refused(self):
        with self.assertRaises(v.CanonicalizationError):
            v.jcs({"n": 2 ** 53 + 1})

    def test_non_finite_refused(self):
        for x in (math.nan, math.inf):
            with self.assertRaises(v.CanonicalizationError):
                v.jcs([x])

    def test_negative_zero(self):
        self.assertEqual(v.jcs([-0.0, 0]), "[0,0]")


class Recipes(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        shutil.copytree(HERE / "fixtures", self.tmp / "fixtures")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, name, fn):
        p = self.tmp / "fixtures" / name
        d = json.loads(p.read_text()); fn(d); p.write_text(json.dumps(d))

    def errs(self):
        return v.check_recipes(INV, self.tmp)[0]

    def test_package_recipes_verify(self):
        self.assertEqual(self.errs(), [])

    def test_setup_check_diverges_from_cts(self):
        self.edit("F-REVIEWED.recipe.json",
                  lambda d: d["setup_checks"][0].update(predicate="A Result exists."))
        self.assertTrue(any("not carried over" in e for e in self.errs()))

    def test_recipe_missing(self):
        (self.tmp / "fixtures" / "F-SIGNALS.recipe.json").unlink()
        self.assertTrue(any("differ from CTS 2.7" in e for e in self.errs()))

    def test_step_order(self):
        self.edit("F-REVIEWED.recipe.json", lambda d: d["steps"][0].update(after=["review"]))
        self.assertTrue(any("not an earlier step" in e for e in self.errs()))

    def test_undefined_behavior(self):
        self.edit("F-REVIEWED.recipe.json",
                  lambda d: d["behaviors"].update({"cts-scripted-judge@1": "J-PASS-75"}))
        self.assertTrue(any("not defined in the CTS" in e for e in self.errs()))

    def test_typed_arguments(self):
        self.edit("F-REVIEWED.recipe.json", lambda d: d["steps"][1]["arguments"].pop("suite"))
        self.assertTrue(any("'suite' is a required property" in e for e in self.errs()))


class Envelopes(unittest.TestCase):
    def test_invalid_examples_rejected(self):
        for p in sorted((EX / "invalid").glob("*.json")):
            with self.subTest(p.name):
                self.assertTrue(v.schema_errors(v.schema_for(p), json.loads(p.read_text())))

    def test_valid_examples_accepted(self):
        for p in sorted(EX.glob("*.json")):
            with self.subTest(p.name):
                self.assertEqual(v.schema_errors(v.schema_for(p), json.loads(p.read_text())), [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
