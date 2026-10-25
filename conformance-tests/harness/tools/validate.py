#!/usr/bin/env python3
"""Validator for the AQEF CTS Harness Contract package, and verifier of run reports.

Package check (no arguments), from anywhere:
    python3 conformance-tests/harness/tools/validate.py

Verify a run:
    python3 conformance-tests/harness/tools/validate.py \
        --report REPORT.json --manifest MANIFEST.json --evidence-root DIR

Needs jsonschema >= 4.18 (pip install jsonschema). Exit status 0 when every check
holds, 1 otherwise. What is checked is listed in harness-contract.md §18; the unit
tests in test_validate.py exercise every check, valid and invalid.
"""
import argparse, copy, hashlib, json, math, pathlib, re, sys
from decimal import Decimal

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

HERE = pathlib.Path(__file__).resolve().parent.parent           # harness/
CTS = HERE.parent                                                # conformance-tests/
ORDER = ["FAIL", "NOT_RUN", "PASS", "NOT_APPLICABLE"]
STATES = ["verified", "violated", "unverified", "not_applicable"]
CASE_RE = r"CT-[A-Z]{3}-\d{3}(?:\.\d{2})?"


# ===================================================================== schemas
def load_schemas(root=HERE):
    schemas = {}
    for p in sorted((root / "schemas").glob("*.schema.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(s)
        schemas[p.name] = s
    registry = Registry().with_resources(
        [(s["$id"], Resource.from_contents(s)) for s in schemas.values()])
    return schemas, registry


SCHEMAS, REGISTRY = load_schemas()


def schema_errors(name, doc):
    v = Draft202012Validator(SCHEMAS[name], registry=REGISTRY)
    return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
            for e in v.iter_errors(doc)]


# ======================================================== RFC 8785 (JCS)
class CanonicalizationError(ValueError):
    pass


def _jcs_number(x):
    """ECMAScript Number::toString, as RFC 8785 §3.2.2.3 requires."""
    if isinstance(x, bool):
        raise CanonicalizationError("bool is not a number")
    if isinstance(x, int):
        if abs(x) > 2 ** 53:
            raise CanonicalizationError(f"integer {x} is outside the exact IEEE 754 range")
        x = float(x)
    if not math.isfinite(x):
        raise CanonicalizationError("NaN and Infinity have no JSON form")
    if x == 0:
        return "0"                                   # covers -0
    sign = "-" if x < 0 else ""
    d = Decimal(repr(abs(x))).normalize()            # shortest round-trip digits
    digits = "".join(map(str, d.as_tuple().digits))
    k = len(digits)
    n = d.as_tuple().exponent + k                    # value = 0.digits × 10^n
    if k <= n <= 21:
        s = digits + "0" * (n - k)
    elif 0 < n <= 21:
        s = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        s = "0." + "0" * (-n) + digits
    else:
        e = n - 1
        mant = digits[0] + ("." + digits[1:] if k > 1 else "")
        s = f"{mant}e{'+' if e > 0 else '-'}{abs(e)}"
    return sign + s


def _jcs_string(s):
    # json.dumps escapes exactly what RFC 8785 §3.2.2.2 requires when ensure_ascii is
    # off: quote, backslash, \b \f \n \r \t, other controls as lowercase \u00xx.
    return json.dumps(s, ensure_ascii=False)


def jcs(value):
    """RFC 8785 serialization. Object keys are sorted by their UTF-16 code units."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return _jcs_number(value)
    if isinstance(value, str):
        return _jcs_string(value)
    if isinstance(value, list):
        return "[" + ",".join(jcs(v) for v in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value, key=lambda k: k.encode("utf-16-be"))
        return "{" + ",".join(_jcs_string(k) + ":" + jcs(value[k]) for k in keys) + "}"
    raise CanonicalizationError(f"{type(value).__name__} has no JSON form")


# The first two vectors are the examples of RFC 8785 §3.2.2 and §3.2.3; the others
# test ECMAScript number formatting and UTF-16 key order at their edges.
JCS_VECTORS = [
    ({"numbers": [333333333.33333329, 1e30, 4.50, 2e-3, 0.000000000000000000000000001],
      "string": "\u20ac$\u000f\nA'B\"\\\\\"/", "literals": [None, True, False]},
     '{"literals":[null,true,false],"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],'
     '"string":"\u20ac$\\u000f\\nA\'B\\"\\\\\\\\\\"/"}'),
    ({"€": "Euro Sign", "\r": "Carriage Return", "דּ": "Hebrew Letter Dalet With Dagesh",
      "1": "One", "\U0001f600": "Emoji: Grinning Face", "\u0080": "Control",
      "ö": "Latin Small Letter O With Diaeresis"},
     '{"\\r":"Carriage Return","1":"One","\u0080":"Control","ö":"Latin Small Letter O With Diaeresis",'
     '"€":"Euro Sign","\U0001f600":"Emoji: Grinning Face","דּ":"Hebrew Letter Dalet With Dagesh"}'),
    ([-0.0, 1e21, 1e-7, 123456789012345680000.0, 0.000001], '[0,1e+21,1e-7,123456789012345680000,0.000001]'),
    ({"": 1, "\U0001f600": 2}, '{"\U0001f600":2,"":1}'),
]


def jcs_self_test():
    errs = []
    for value, want in JCS_VECTORS:
        got = jcs(value)
        if got != want:
            errs.append(f"JCS vector failed: got {got!r}, want {want!r}")
    return errs


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


# ===================================================================== CTS
def _capability_ids(field):
    field = field.strip()
    ids = re.findall(r"`([^`]+)`", field)
    return ids or [field.split(";")[0].strip()]


def load_inventory(cts=CTS):
    """Tests, cases, capabilities, requirement traces, fixtures, and behavior codes,
    read from the CTS text itself."""
    inv = {"tests": {}, "requirements": {}, "fixtures": {}}
    status = (cts / "00-introduction.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Status:\*\* Working Draft (\d+)\.", status)
    cr = re.search(r"\*\*Status:\*\* Candidate Recommendation \d+ \(([0-9.]+-CR\d+)\)\.", status)
    inv["revision"] = f"WD{m.group(1)}" if m else (cr.group(1) if cr else None)
    text = ""
    for f in sorted(cts.glob("[0-9]*.md")):
        t = f.read_text(encoding="utf-8")
        text += t + "\n"
        if not re.match(r"[12]\d-", f.name):
            continue
        for b in re.finditer(r"^### (CT-[A-Z]{3}-\d{3}) .*?(?=^### |^## |\Z)", t, re.S | re.M):
            tid, body = b.group(1), b.group(0)
            cap = re.search(r"^- \*\*Capability:\*\* (.*)$", body, re.M).group(1)
            cases = re.findall(r"^\| `(" + tid + r"\.\d{2})` \|", body, re.M)
            per_case = {}
            for cid in cases:
                cm = re.search(r"case `" + re.escape(cid) + r"`: `([^`]+)`", cap)
                per_case[cid] = [cm.group(1)] if cm else ["core"]
            base_caps = _capability_ids(cap.split(";")[0])
            inv["tests"][tid] = {
                "capability": base_caps,
                "cases": cases or [tid],
                "case_caps": per_case or {tid: base_caps},
            }
    trace = (cts / "90-traceability.md").read_text(encoding="utf-8")
    sec = re.search(r"## 90\.3.*?\n(.*?)\n## 90\.4", trace, re.S).group(1)
    raw = {}
    for row in re.findall(r"^\| (R-\d{4}) \| [^|]* \| ([^|]+) \| ([^|]*) \|$", sec, re.M):
        rid, st, note = row[0], row[1].strip(), row[2]
        raw[rid] = (st, note)
    for rid, (st, note) in raw.items():
        if st == "Tested":
            inv["requirements"][rid] = {"traced": re.findall(CASE_RE, note.split(";")[0]),
                                        "derived_from": None}
        elif st == "Restates":
            src = re.match(r"(R-\d{4})", note.strip()).group(1)
            inv["requirements"][rid] = {"traced": None, "derived_from": src}
    # A Restates row takes the trace of the row it restates; one that restates a row
    # not listed (Not testable) is not listed either.
    for rid in [r for r, q in inv["requirements"].items() if q["derived_from"]]:
        src = inv["requirements"].get(inv["requirements"][rid]["derived_from"])
        if src is None or src["derived_from"]:
            del inv["requirements"][rid]
        else:
            inv["requirements"][rid]["traced"] = src["traced"]
    table = re.search(r"## 2\.7 Postcondition fixtures(.*?)\n## ",
                      (cts / "02-fixtures.md").read_text(encoding="utf-8"), re.S).group(1)
    for row in re.findall(r"^\| (F-[A-Z-]+) \| (.*?) \| (.*?) \|$", table, re.M):
        inv["fixtures"][row[0]] = [s.strip() for s in re.split(r"(?<=\.) |; ", row[2]) if s.strip()]
    inv["codes"] = set(re.findall(r"`((?:SR|J)-[A-Z0-9-]+)(?:\(|`)", text))
    contract = (HERE / "harness-contract.md").read_text(encoding="utf-8")
    inv["local_codes"] = set(re.findall(r"`(H-[A-Z0-9-]+)`", contract))
    return inv


def all_cases(inv):
    return {c: t for t, d in inv["tests"].items() for c in d["cases"]}


def is_claimed(caps, claims):
    """Every identifier must be claimed; `core` always is; `x:<...>` is claimed by any
    claim starting with `x:`."""
    for c in caps:
        if c == "core":
            continue
        if c.endswith(">") and ":<" in c:
            if not any(cl.startswith(c.split(":<")[0] + ":") for cl in claims):
                return False
        elif c not in claims:
            return False
    return True


# ===================================================================== algebra
def summarize(outcomes):
    for o in ORDER[:3]:
        if o in outcomes:
            return o
    return "NOT_APPLICABLE"


def requirement_state(traced, case_outcome):
    outs = [case_outcome.get(c, "NOT_RUN") for c in traced]
    applicable = [o for o in outs if o != "NOT_APPLICABLE"]
    if "FAIL" in applicable:
        return "violated"
    if "NOT_RUN" in applicable:
        return "unverified"
    if "PASS" in applicable:
        return "verified"
    return "not_applicable"


def _dupes(seq):
    seen, out = set(), set()
    for x in seq:
        (out if x in seen else seen).add(x)
    return sorted(out)


# ===================================================================== report
def check_report(r, inv, manifest=None, evidence_root=None):
    errs = list(schema_errors("cts-report.schema.json", r))
    if errs:
        return errs
    cases_by_id = {}
    for d in _dupes([c["case_id"] for c in r["cases"]]):
        errs.append(f"case {d} reported more than once")
    for d in _dupes([t["test_id"] for t in r["tests"]]):
        errs.append(f"test {d} reported more than once")
    for d in _dupes([q["requirement_id"] for q in r["requirements"]]):
        errs.append(f"requirement {d} reported more than once")
    for c in r["cases"]:
        cases_by_id.setdefault(c["case_id"], c)
    case_outcome = {k: v["outcome"] for k, v in cases_by_id.items()}

    # provenance
    if r["provenance"]["cts_revision"] != inv["revision"]:
        errs.append(f"report is for CTS {r['provenance']['cts_revision']}, "
                    f"the CTS here is {inv['revision']}")

    # plan and completeness
    plan = r["plan"]
    planned = plan["test_ids"]
    for d in _dupes(planned):
        errs.append(f"plan lists {d} more than once")
    unknown = sorted(set(planned) - set(inv["tests"]))
    if unknown:
        errs.append(f"plan names tests not in the CTS: {unknown}")
    if plan["scope"] == "full" and set(planned) != set(inv["tests"]):
        errs.append(f"plan is full but omits {len(set(inv['tests']) - set(planned))} tests")
    if plan["scope"] == "partial" and set(planned) == set(inv["tests"]):
        errs.append("plan lists every test but is marked partial")
    reported_tests = {t["test_id"] for t in r["tests"]}
    if reported_tests != set(planned):
        errs.append(f"tests reported differ from plan: missing "
                    f"{sorted(set(planned) - reported_tests)}, extra {sorted(reported_tests - set(planned))}")
    want_cases = {c for t in planned if t in inv["tests"] for c in inv["tests"][t]["cases"]}
    if set(cases_by_id) != want_cases:
        errs.append(f"cases reported differ from plan: missing "
                    f"{sorted(want_cases - set(cases_by_id))}, extra {sorted(set(cases_by_id) - want_cases)}")

    # tests and cases against the CTS
    claims = r["provenance"].get("capabilities_claimed", [])
    for t in r["tests"]:
        tid = t["test_id"]
        if tid not in inv["tests"]:
            continue
        if t["case_ids"] != inv["tests"][tid]["cases"]:
            errs.append(f"{tid}: case_ids differ from the CTS")
        outs = [case_outcome.get(c) for c in t["case_ids"]]
        if None not in outs and t["outcome"] != summarize(outs):
            errs.append(f"{tid}: outcome {t['outcome']}, its cases give {summarize(outs)}")
    owner = all_cases(inv)
    for cid, c in cases_by_id.items():
        if cid not in owner:
            errs.append(f"case {cid} is not in the CTS")
            continue
        tid = owner[cid]
        if c["test_id"] != tid:
            errs.append(f"case {cid} names test {c['test_id']}, the CTS puts it in {tid}")
        caps = inv["tests"][tid]["case_caps"][cid]
        if c["capability"] != " + ".join(caps):
            errs.append(f"case {cid}: capability {c['capability']!r}, the CTS gives {' + '.join(caps)!r}")
        claimed = is_claimed(caps, claims)
        if c["reason_code"] == "CAPABILITY_NOT_CLAIMED" and claimed:
            errs.append(f"case {cid}: CAPABILITY_NOT_CLAIMED, but its capability is claimed")
        if not claimed and c["outcome"] != "NOT_APPLICABLE":
            errs.append(f"case {cid}: capability not claimed, outcome must be NOT_APPLICABLE")

    # requirements
    want_reqs = inv["requirements"]
    got_reqs = {q["requirement_id"]: q for q in r["requirements"]}
    if set(got_reqs) != set(want_reqs):
        errs.append(f"requirements differ from Section 90: missing "
                    f"{sorted(set(want_reqs) - set(got_reqs))[:5]}..., "
                    f"extra {sorted(set(got_reqs) - set(want_reqs))[:5]}")
    for rid, q in got_reqs.items():
        w = want_reqs.get(rid)
        if not w:
            continue
        if sorted(q["traced_to"]) != sorted(w["traced"]):
            errs.append(f"{rid}: traced_to differs from Section 90")
        if q.get("derived_from") != w["derived_from"]:
            errs.append(f"{rid}: derived_from differs from Section 90")
        want = requirement_state(w["traced"], case_outcome)
        if q["state"] != want:
            errs.append(f"{rid}: state {q['state']}, the algebra gives {want}")

    # summary
    def count(items, key, keys):
        return {k: sum(1 for i in items if i[key] == k) for k in keys}
    s = r["summary"]
    if s["cases"] != count(r["cases"], "outcome", ORDER):
        errs.append("summary.cases does not match cases")
    if s["tests"] != count(r["tests"], "outcome", ORDER):
        errs.append("summary.tests does not match tests")
    if s["requirements"] != count(r["requirements"], "state", STATES):
        errs.append("summary.requirements does not match requirements")

    # reviews
    review_ids = {m["review_id"] for m in r.get("manual_reviews", [])}
    for c in r["cases"]:
        for rid in c.get("review_ids", []):
            if rid not in review_ids:
                errs.append(f"case {c['case_id']} names review {rid}, which the report lacks")

    # evidence
    if manifest is not None:
        errs += check_manifest(manifest, evidence_root)
        if manifest.get("run_id") != r["run_id"]:
            errs.append("manifest and report have different run_id")
        if manifest.get("manifest_sha256") != r["evidence_manifest_sha256"]:
            errs.append("report's evidence_manifest_sha256 does not match the manifest")
        known = {e["raw_ref"] for e in manifest["entries"]} | \
                {e["redacted_ref"] for e in manifest["entries"] if "redacted_ref" in e}
        refs = [x for c in r["cases"] for x in c["evidence_refs"]]
        refs += [x for m in r.get("manual_reviews", []) for i in m["checklist"] for x in i["evidence_refs"]]
        refs.append(r["provenance"]["conformance_statement_ref"])
        missing = sorted(set(refs) - known)
        if missing:
            errs.append(f"evidence referenced but not in the manifest: {missing}")
    return errs


# ===================================================================== evidence
def resolve(ref, root):
    if not ref.startswith("evidence://"):
        raise ValueError(f"{ref}: only evidence:// references resolve in a directory store")
    p = (root / ref[len("evidence://"):]).resolve()
    if root.resolve() not in p.parents:
        raise ValueError(f"{ref}: resolves outside the evidence root")
    return p


def check_manifest(m, evidence_root=None):
    errs = list(schema_errors("evidence-manifest.schema.json", m))
    if errs:
        return errs
    for d in _dupes([e["evidence_id"] for e in m["entries"]]):
        errs.append(f"evidence {d} listed more than once")
    for d in _dupes([e["raw_ref"] for e in m["entries"]]):
        errs.append(f"raw_ref {d} listed more than once")
    try:
        body = {k: v for k, v in m.items() if k != "manifest_sha256"}
        if sha256_hex(jcs(body).encode("utf-8")) != m["manifest_sha256"]:
            errs.append("manifest_sha256 does not verify")
    except CanonicalizationError as e:
        errs.append(f"manifest cannot be canonicalized: {e}")
    if evidence_root is None:
        return errs
    root = pathlib.Path(evidence_root)
    for e in m["entries"]:
        for kind in ("raw", "redacted"):
            ref = e.get(f"{kind}_ref")
            if ref is None:
                continue
            try:
                p = resolve(ref, root)
            except ValueError as x:
                errs.append(str(x))
                continue
            if not p.is_file():
                errs.append(f"{e['evidence_id']}: {kind} object {ref} is missing")
                continue
            data = p.read_bytes()
            if sha256_hex(data) != e[f"{kind}_sha256"]:
                errs.append(f"{e['evidence_id']}: {kind} object {ref} does not match its digest")
            if kind == "raw" and len(data) != e["raw_size"]:
                errs.append(f"{e['evidence_id']}: raw object {ref} is {len(data)} bytes, "
                            f"the manifest says {e['raw_size']}")
    return errs


# ===================================================================== package
def check_recipes(inv, root=HERE):
    errs, recipes = [], {}
    ops = SCHEMAS["adapter-operation.schema.json"]["$defs"]["args"]
    for p in sorted((root / "fixtures").glob("*.recipe.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        errs += [f"fixtures/{p.name}: {e}" for e in schema_errors("fixture-recipe.schema.json", doc)]
        recipes[doc["fixture_id"]] = doc
        ids = [s["step_id"] for s in doc["steps"]]
        errs += [f"fixtures/{p.name}: duplicate step {d}" for d in _dupes(ids)]
        seen = set()
        for s in doc["steps"]:
            for a in s.get("after", []):
                if a not in seen:
                    errs.append(f"fixtures/{p.name}: step {s['step_id']} runs after {a}, "
                                "which is not an earlier step")
            seen.add(s["step_id"])
            if s["operation"] in ops:
                sch = dict(ops[s["operation"]])
                sch["$id"] = SCHEMAS["adapter-operation.schema.json"]["$id"]
                for e in Draft202012Validator(sch, registry=REGISTRY).iter_errors(s["arguments"]):
                    errs.append(f"fixtures/{p.name}: step {s['step_id']}: {e.message}")
            if s["operation"] == "configure_behavior":
                errs += check_code(f"fixtures/{p.name}", s["arguments"]["behavior"], inv)
        for code in doc.get("behaviors", {}).values():
            errs += check_code(f"fixtures/{p.name}", code, inv)
        for c in doc["setup_checks"]:
            if c.get("from_step") and c["from_step"] not in ids:
                errs.append(f"fixtures/{p.name}: check {c['check_id']} names an unknown step")
    if set(recipes) != set(inv["fixtures"]):
        errs.append(f"recipes {sorted(recipes)} differ from CTS 2.7 {sorted(inv['fixtures'])}")
    norm = lambda s: s.replace("`", "").rstrip(".").strip().lower()
    for fid, sentences in inv["fixtures"].items():
        if fid in recipes:
            preds = " ".join(norm(c["predicate"]) for c in recipes[fid]["setup_checks"])
            errs += [f"fixtures/{fid}: CTS setup check not carried over: {s}"
                     for s in sentences if norm(s) not in preds]
    return errs, recipes


def check_code(where, code, inv):
    errs = []
    base = code.split("(")[0]
    if base.startswith("H-"):
        if base not in inv["local_codes"]:
            errs.append(f"{where}: harness-local behavior {base} is not defined in the contract")
    elif base not in inv["codes"]:
        errs.append(f"{where}: behavior {base} is not defined in the CTS")
    for inner in re.findall(r"((?:SR|J|H)-[A-Z0-9-]+)", code[len(base):]):
        errs += check_code(where, inner, inv)
    return errs


def schema_for(path):
    return path.name.split("--")[0] + ".schema.json"


def check_package(root=HERE):
    inv = load_inventory()
    errs = jcs_self_test()
    plain = sorted(p for p in (root / "examples").glob("*.json")
                   if schema_for(p) not in ("cts-report.schema.json", "evidence-manifest.schema.json"))
    for p in plain:
        errs += [f"examples/{p.name}: {e}" for e in schema_errors(schema_for(p), json.loads(p.read_text()))]
        doc = json.loads(p.read_text())
        if doc.get("operation") == "configure_behavior":
            errs += check_code(f"examples/{p.name}", doc["arguments"]["behavior"], inv)
    for p in sorted((root / "examples").glob("cts-report--*.json")):
        name = p.name.split("--", 1)[1]
        mp = root / "examples" / f"evidence-manifest--{name}"
        manifest = json.loads(mp.read_text()) if mp.exists() else None
        if manifest is None:
            errs.append(f"examples/{p.name}: no evidence-manifest--{name}")
        errs += [f"examples/{p.name}: {e}" for e in
                 check_report(json.loads(p.read_text()), inv, manifest, root / "examples" / "evidence")]
    for p in sorted((root / "examples" / "invalid").glob("*.json")):
        if not schema_errors(schema_for(p), json.loads(p.read_text())):
            errs.append(f"examples/invalid/{p.name}: accepted, but must be rejected")
    rerrs, recipes = check_recipes(inv, root)
    errs += rerrs
    return errs, {"schemas": len(SCHEMAS), "examples": len(list((root / "examples").glob("*.json"))),
                  "rejected": len(list((root / "examples" / "invalid").glob("*.json"))),
                  "recipes": len(recipes)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report")
    ap.add_argument("--manifest")
    ap.add_argument("--evidence-root")
    a = ap.parse_args(argv)
    if a.report:
        if not (a.manifest and a.evidence_root):
            ap.error("--report needs --manifest and --evidence-root: a run is verified "
                     "with its evidence, never without it")
        r = json.loads(pathlib.Path(a.report).read_text(encoding="utf-8"))
        m = json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
        errs = check_report(r, load_inventory(), m, a.evidence_root)
        summary = f"OK: report {r['run_id']} verified with its evidence"
    else:
        errs, n = check_package()
        summary = (f"OK: {n['schemas']} schemas, {n['examples']} examples, "
                   f"{n['rejected']} rejected examples, {n['recipes']} recipes, "
                   f"{len(JCS_VECTORS)} JCS vectors")
    if errs:
        print("\n".join(errs))
        print(f"{len(errs)} problem(s)")
        return 1
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
