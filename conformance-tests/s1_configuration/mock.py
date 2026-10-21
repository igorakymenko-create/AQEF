"""Non-normative minimal S1 mock SUT: not an AQEF implementation."""
from __future__ import annotations
import copy


def fixture_base():
    return {'project':{'name':'cts-base','environments':[{'name':'cts-env','model_version':'cts-scripted-subject@1','prompt_version':'cts-prompt@1','tool_configuration':None,'infra_target':'cts-harness'}], 'quality_gates':[{'name':'functional-gate','aggregate':'functional','threshold':1.0,'on_failure':'block_release'}], 'suites':[{'name':'cts-suite','scenarios':[{'name':'s-greeting','variables':{'query':'Hello'},'prompt':{'template':'{{query}}'},'contract':{'constraints':[{'validator':'schema','target':'response','expected':{'type':'string','minLength':1}}],'expectations':[{'criteria':'The response greets the user.','judge':{'model':'cts-scripted-judge@1','confidence_source':'self_rating'},'confidence_threshold':0.8}]}}]}]}}


def fixture_seed():
    """Minimal F-SEED project extension used only to exercise missing defect_classes[0].name."""
    c=fixture_base()
    c['project']['defect_classes']=[{'name':'cts-defect'}]
    return c

class MockSUT:
    def __init__(self, mutation=None, capabilities=()):
        self.mutation=mutation
        self.capabilities=set(capabilities)
        self.projects={}

    def load(self, project_id, config):
        if not isinstance(config,dict) or not isinstance(config.get('project'),dict):
            return 422,{'code':'INVALID_CONFIG','field':'project'}
        project=config['project']
        mandatory=[('project.name',project,'name')]
        if isinstance(project.get('environments'),list) and project['environments']:
            mandatory.append(('environments[0].tool_configuration',project['environments'][0],'tool_configuration'))
        else:
            return 422,{'code':'INVALID_CONFIG','field':'environments'}
        if 'seeded_controls' in self.capabilities and 'defect_classes' in project:
            if not isinstance(project['defect_classes'],list) or not project['defect_classes']:
                return 422,{'code':'INVALID_CONFIG','field':'defect_classes'}
            mandatory.append(('defect_classes[0].name',project['defect_classes'][0],'name'))
        for path,obj,key in mandatory:
            if key not in obj or (obj[key] is None and key!='tool_configuration'):
                if self.mutation=='accept_missing_'+key:
                    continue
                if self.mutation=='vague_error':
                    return 422,{'code':'INVALID_CONFIG','detail':'invalid'}
                return 422,{'code':'INVALID_CONFIG','field':path,'detail':'required field missing'}
        if self.mutation=='reject_valid':return 422,{'code':'INVALID_CONFIG','field':'project.name'}
        stored=copy.deepcopy(config)
        if self.mutation=='drop_tool_configuration':
            stored['project']['environments'][0].pop('tool_configuration',None)
        self.projects[project_id]=stored
        return 201,{'project_id':project_id,'config':copy.deepcopy(stored)}

    def get(self, project_id):
        if project_id not in self.projects:return 404,{'code':'NOT_FOUND'}
        return 200,{'config':copy.deepcopy(self.projects[project_id])}
