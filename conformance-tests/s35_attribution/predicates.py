"""S3.5.4 Q-02/Q-08: explicit allowlisted field paths and typed predicates.

No eval or arbitrary Python access. Predicates are runner-maintained and
independently applied to resolved, hash-verified data. NOT normative test text.
"""
from __future__ import annotations
import re

# All paths refer to JSON document returned by S3.5.4 mock operation readback.
PATHS={
  'execution.ids':('execution_ids',),
  'conversation.execution':('execution_id',),
  'conversation.messages':('conversation','messages'),
  'results.execution':('execution_id',),
  'results.rows':('results',),
  'results.effective_judge':('effective','expectation-1'),
  'results.effective_validator':('effective','schema'),
  'gate.execution':('execution_id',),
  'gate.status':('gate','status'),
  'gate.reasons':('gate','reasons'),
  'gate.basis.results':('gate','basis','results'),
  'gate.basis.not_actionable':('gate','basis','not_actionable'),
  'gate.id':('gate','id'),
  'review.accepted':('accepted',),
  'approval.accepted':('accepted',),
  'release.accepted':('accepted',),
}
ALLOWED_COMPARATORS={'eq','ne','len_eq','contains','unique_ids'}


def resolve_path(body,alias):
    if alias not in PATHS:raise KeyError('UNSUPPORTED_FIELD_PATH')
    cur=body
    for part in PATHS[alias]:
        if not isinstance(cur,dict) or part not in cur:raise KeyError('FIELD_MISSING')
        cur=cur[part]
    return cur


def evaluate(body,spec):
    if not isinstance(spec,dict) or set(spec)!={'field','op','expected'}:
        return {'outcome':'NOT_RUN','reason':'PREDICATE_INVALID'}
    alias,op,expected=spec['field'],spec['op'],spec['expected']
    if not isinstance(alias,str) or op not in ALLOWED_COMPARATORS:
        return {'outcome':'NOT_RUN','reason':'PREDICATE_UNSUPPORTED'}
    try:actual=resolve_path(body,alias)
    except KeyError:return {'outcome':'NOT_RUN','reason':'FIELD_UNAVAILABLE'}
    if op=='eq':good=type(actual)==type(expected) and actual==expected
    elif op=='ne':good=type(actual)!=type(expected) or actual!=expected
    elif op=='len_eq':good=isinstance(actual,(list,dict)) and type(expected)==int and len(actual)==expected
    elif op=='contains':good=isinstance(actual,list) and expected in actual
    elif op=='unique_ids':good=(isinstance(actual,list) and expected is True and
             all(isinstance(v,dict) and isinstance(v.get('id'),str) for v in actual) and
             len({v['id'] for v in actual})==len(actual))
    else:good=False
    return {'outcome':'PASS' if good else 'FAIL',
            'reason':'EXPECTED_MET' if good else 'EXPECTED_VIOLATED'}


def all_of(body,predicates):
    if not isinstance(predicates,list) or not predicates:return {'outcome':'NOT_RUN','reason':'PREDICATES_MISSING'}
    evaluations=[evaluate(body,p) for p in predicates]
    outcome='NOT_RUN' if any(x['outcome']=='NOT_RUN' for x in evaluations) else ('FAIL' if any(x['outcome']=='FAIL' for x in evaluations) else 'PASS')
    return {'outcome':outcome,'checks':evaluations}

Q08={
 'CT-EXE-008:get_conversation':[{'field':'conversation.messages','op':'len_eq','expected':2}],
 'CT-DEC-006:evaluate_gates':[{'field':'gate.status','op':'eq','expected':'fail'},
   {'field':'gate.reasons','op':'contains','expected':'non_actionable_results'},
   {'field':'gate.basis.not_actionable','op':'eq','expected':1}],
 'CT-DEC-012:get_results':[{'field':'results.rows','op':'unique_ids','expected':True},
   {'field':'results.rows','op':'len_eq','expected':2}],
 'CT-REL-006:evaluate_gates':[{'field':'gate.status','op':'eq','expected':'fail'},
   {'field':'gate.reasons','op':'contains','expected':'aggregate_failed'}],
}
