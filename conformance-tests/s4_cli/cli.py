"""Stage C S4.2 reference CLI, a thin Appendix C REST wrapper (mock scope only)."""
from __future__ import annotations
import argparse, json, sys, urllib.request, urllib.error

DOCUMENTED_COMMANDS = {'load-config': 'load_config', 'execute': 'execute', 'evaluate-gates': 'evaluate_gates'}

def request(url, operation, arguments):
    body=json.dumps({'operation':operation,'arguments':arguments}).encode()
    req=urllib.request.Request(url, data=body, headers={'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req,timeout=4) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError('REST_ERROR:'+str(exc.code)) from exc

def main(argv=None):
    p=argparse.ArgumentParser(description='Mock-only Stage C CLI REST adapter')
    p.add_argument('--api',required=True)
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('load-config');a.add_argument('--project-id',required=True);a.add_argument('--fixture',required=True)
    b=sub.add_parser('execute');b.add_argument('--project-id',required=True);b.add_argument('--suite',required=True);b.add_argument('--environment',required=True)
    c=sub.add_parser('evaluate-gates');c.add_argument('--project-id',required=True);c.add_argument('--batch-id',required=True)
    opt=p.parse_args(argv)
    if opt.command=='load-config':
        with open(opt.fixture,encoding='utf8') as f: config=json.load(f)
        args={'project_id':opt.project_id,'config':config}
    elif opt.command=='execute': args={'project_id':opt.project_id,'suite':opt.suite,'environment':opt.environment}
    else:args={'project_id':opt.project_id,'batch_id':opt.batch_id}
    try:
        reply=request(opt.api,DOCUMENTED_COMMANDS[opt.command],args)
        print(json.dumps(reply,sort_keys=True));return 0
    except (RuntimeError,OSError,ValueError) as e:
        print(str(e),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
