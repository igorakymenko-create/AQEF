"""Auditable, evidence-based S2/S3 re-audit readiness register.

NO auto-acceptance from successful unit tests; explicit boundaries stay OPEN.
"""
from __future__ import annotations
import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parent

def register():
    return json.loads((ROOT/'audit_register.json').read_text(encoding='utf-8'))

def summarize(items=None):
    items=items or register()
    if len({i['id'] for i in items})!=len(items):raise ValueError('duplicate audit finding')
    allowed={'MOCK_CLOSED_PENDING_CI','OPEN','PARTIAL','DEFERRED'}
    if any(i['status'] not in allowed for i in items):raise ValueError('unsupported status')
    return {'total':len(items),'mock_closed_pending_ci':sum(i['status']=='MOCK_CLOSED_PENDING_CI' for i in items),
            'open_or_partial':sum(i['status'] in ('OPEN','PARTIAL') for i in items),
            'items':[{'id':i['id'],'status':i['status']} for i in items],
            'real_sut_conformance':False,'unconditional_exit_acceptance':False}
