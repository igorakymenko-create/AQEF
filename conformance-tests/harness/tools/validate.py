#!/usr/bin/env python3
"""Consistency check for the AQEF CTS Harness Contract package.

Run from anywhere:  python3 conformance-tests/harness/tools/validate.py
Needs: jsonschema >= 4.18 (pip install jsonschema).

Checks
  1. every schema is a valid JSON Schema 2020-12 document;
  2. every file in examples/ validates against the schema its name starts with,
     and passes the report and manifest invariants below;
  3. every file in examples/invalid/ is rejected, by its schema or an invariant;
  4. every recipe in fixtures/ validates, its steps form an acyclic graph, the
     arguments of typed operations validate, and the set of recipes and their
     setup checks match the table of CTS section 2.7;
  5. every behavior code used is defined in the CTS or in the contract (H-...).
Exit status 0 when everything holds, 1 otherwise.
"""
import json, hashlib, pathlib, re, sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

HERE = pathlib.Path(__file__).resolve().parent.parent          # harness/
CTS = HERE.parent                                               # conformance-tests/
problems = []


def bad(msg):
    problems.append(msg)


# ---------- schemas --------------------------------------------------------
schemas = {}
for p in sorted((HERE / "schemas").glob("*.schema.json")):
    s = json.loads(p.read_text())
    Draft202012Validator.check_schema(s)
    schemas[p.name] = s
registry = Registry().with_resources(
    [(s["$id"], Resource.from_contents(s)) for s in schemas.values()])


def validator(name):
    return Draft202012Validator(schemas[name], registry=registry)


def schema_errors(name, doc):
    return [e.message for e in validator(name).iter_errors(doc)]


# ---------- invariants -----------------------------------------------------
ORDER = ["FAIL", "NOT_RUN", "PASS", "NOT_APPLICABLE"]


def summarize(outcomes):
    """CTS 1.2, Cases: FAIL, else NOT_RUN, else PASS, else NOT_APPLICABLE."""
    for o in ORDER[:3]:
        if o in outcomes:
            return o
    return "NOT_APPLICABLE"


def requirement_state(traced, case_outcome):
    """Contract §14.3: applicable entries exclude NOT_APPLICABLE; a traced
    entry missing from the run counts as NOT_RUN."""
    outs = [case_outcome.get(c, "NOT_RUN") for c in traced]
    applicable = [o for o in outs if o != "NOT_APPLICABLE"]
    if "FAIL" in applicable:
        return "violated"
    if "NOT_RUN" in applicable:
        return "unverified"
    if "PASS" in applicable:
        return "verified"
    return "not_applicable"


def report_invariants(r):
    errs = []
    case_outcome = {c["case_id"]: c["outcome"] for c in r["cases"]}
    for t in r["tests"]:
        missing = [c for c in t["case_ids"] if c not in case_outcome]
        if missing:
            errs.append(f"{t['test_id']}: cases not reported {missing}")
            continue
        want = summarize([case_outcome[c] for c in t["case_ids"]])
        if t["outcome"] != want:
            errs.append(f"{t['test_id']}: outcome {t['outcome']}, cases give {want}")
    for q in r["requirements"]:
        want = requirement_state(q["traced_to"], case_outcome)
        if q["state"] != want:
            errs.append(f"{q['requirement_id']}: state {q['state']}, algebra gives {want}")
    def count(items, key, keys):
        return {k: sum(1 for i in items if i[key] == k) for k in keys}
    s = r["summary"]
    if s["cases"] != count(r["cases"], "outcome", ORDER):
        errs.append("summary.cases does not match cases")
    if s["tests"] != count(r["tests"], "outcome", ORDER):
        errs.append("summary.tests does not match tests")
    if s["requirements"] != count(r["requirements"], "state",
                                  ["verified", "violated", "unverified", "not_applicable"]):
        errs.append("summary.requirements does not match requirements")
    return errs


def jcs(obj):
    # RFC 8785 for documents holding strings, integers, booleans, null, lists and
    # objects only (no non-integer numbers), which is all a manifest holds.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def manifest_invariants(m):
    body = {k: v for k, v in m.items() if k != "manifest_sha256"}
    h = hashlib.sha256(jcs(body).encode("utf-8")).hexdigest()
    return [] if h == m["manifest_sha256"] else ["manifest_sha256 does not verify"]


def invariants(schema, doc):
    if schema == "cts-report.schema.json":
        return report_invariants(doc)
    if schema == "evidence-manifest.schema.json":
        return manifest_invariants(doc)
    return []


def schema_for(path):
    prefix = path.name.split("--")[0]
    return prefix + ".schema.json"


# ---------- examples -------------------------------------------------------
for p in sorted((HERE / "examples").glob("*.json")):
    sname = schema_for(p)
    doc = json.loads(p.read_text())
    errs = schema_errors(sname, doc)
    if not errs:
        errs = invariants(sname, doc)
    for e in errs:
        bad(f"examples/{p.name}: {e}")

for p in sorted((HERE / "examples" / "invalid").glob("*.json")):
    sname = schema_for(p)
    doc = json.loads(p.read_text())
    if not schema_errors(sname, doc) and not invariants(sname, doc):
        bad(f"examples/invalid/{p.name}: accepted, but must be rejected")

# ---------- behavior codes -------------------------------------------------
cts_text = "\n".join(p.read_text() for p in sorted(CTS.glob("[0-9]*.md")))
cts_codes = set(re.findall(r"`((?:SR|J)-[A-Z0-9-]+)(?:\(|`)", cts_text))
contract_text = (HERE / "harness-contract.md").read_text()
local_codes = set(re.findall(r"`(H-[A-Z0-9-]+)`", contract_text))


def check_code(where, code):
    base = code.split("(")[0]
    if base.startswith("H-"):
        if base not in local_codes:
            bad(f"{where}: harness-local behavior {base} is not defined in the contract")
    elif base not in cts_codes:
        bad(f"{where}: behavior {base} is not defined in the CTS")
    for inner in re.findall(r"((?:SR|J|H)-[A-Z0-9-]+)", code[len(base):]):
        check_code(where, inner)


# ---------- fixtures -------------------------------------------------------
ops_schema = schemas["adapter-operation.schema.json"]["$defs"]["args"]
fixture_table = re.search(r"## 2\.7 Postcondition fixtures(.*?)\n## ",
                          (CTS / "02-fixtures.md").read_text(), re.S).group(1)
cts_fixtures = {}
for row in re.findall(r"^\| (F-[A-Z-]+) \| (.*?) \| (.*?) \|$", fixture_table, re.M):
    cts_fixtures[row[0]] = [s.strip() for s in re.split(r"(?<=\.) |; ", row[2]) if s.strip()]

recipes = {}
for p in sorted((HERE / "fixtures").glob("*.recipe.json")):
    doc = json.loads(p.read_text())
    for e in schema_errors("fixture-recipe.schema.json", doc):
        bad(f"fixtures/{p.name}: {e}")
    recipes[doc["fixture_id"]] = doc
    ids = [s["step_id"] for s in doc["steps"]]
    if len(ids) != len(set(ids)):
        bad(f"fixtures/{p.name}: duplicate step_id")
    seen = set()
    for s in doc["steps"]:
        for a in s.get("after", []):
            if a not in seen:
                bad(f"fixtures/{p.name}: step {s['step_id']} runs after {a}, "
                    "which is not an earlier step")
        seen.add(s["step_id"])
        if s["operation"] in ops_schema:
            sch = dict(ops_schema[s["operation"]])
            sch["$id"] = schemas["adapter-operation.schema.json"]["$id"]
            v = Draft202012Validator(sch, registry=registry)
            for e in v.iter_errors(s["arguments"]):
                bad(f"fixtures/{p.name}: step {s['step_id']}: {e.message}")
        if s["operation"] == "configure_behavior":
            check_code(f"fixtures/{p.name}", s["arguments"]["behavior"])
    for code in doc.get("behaviors", {}).values():
        check_code(f"fixtures/{p.name}", code)
    for c in doc["setup_checks"]:
        if c.get("from_step") and c["from_step"] not in ids:
            bad(f"fixtures/{p.name}: check {c['check_id']} names unknown step")

if set(recipes) != set(cts_fixtures):
    bad(f"recipes {sorted(recipes)} differ from CTS 2.7 {sorted(cts_fixtures)}")
for fid, sentences in cts_fixtures.items():
    if fid in recipes:
        def norm(s):
            return s.replace("`", "").rstrip(".").strip().lower()
        preds = " ".join(norm(c["predicate"]) for c in recipes[fid]["setup_checks"])
        for sentence in sentences:
            if norm(sentence) not in preds:
                bad(f"fixtures/{fid}: CTS setup check not carried over: {sentence}")

for p in sorted((HERE / "examples").glob("adapter-operation--*.json")):
    doc = json.loads(p.read_text())
    if doc["operation"] == "configure_behavior":
        check_code(f"examples/{p.name}", doc["arguments"]["behavior"])

# ---------- result ---------------------------------------------------------
if problems:
    print("\n".join(problems))
    print(f"{len(problems)} problem(s)")
    sys.exit(1)
print(f"OK: {len(schemas)} schemas, "
      f"{len(list((HERE / 'examples').glob('*.json')))} examples, "
      f"{len(list((HERE / 'examples' / 'invalid').glob('*.json')))} rejected examples, "
      f"{len(recipes)} recipes")
