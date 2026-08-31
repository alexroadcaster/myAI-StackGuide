"""Bounded public GitHub collection, one repository and checkpointed block at a time.

CAT-03: normalized review artifacts only. Never writes the canonical catalog or
uses credentials. CAT-04 must prove a real card before a full-corpus run.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.github.com'
API_VERSION = '2026-03-10'
NAME = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
MANIFEST_NAMES = {'package.json','pyproject.toml','requirements.txt','Cargo.toml','go.mod','pom.xml','build.gradle','Gemfile','composer.json','pubspec.yaml','Dockerfile'}
FACTS = {
    'githubRepositoryId':'id','fullName':'full_name','url':'html_url','stars':'stargazers_count',
    'forks':'forks_count','watchers':'subscribers_count','sizeKb':'size','archived':'archived',
    'isFork':'fork','disabled':'disabled','visibility':'visibility','defaultBranch':'default_branch',
    'language':'language','description':'description','topics':'topics','homepage':'homepage',
    'activity.createdAt':'created_at','activity.updatedAt':'updated_at','activity.pushedAt':'pushed_at',
}


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.tmp')
    with temporary.open('w',encoding='utf-8',newline='\n') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    os.replace(temporary, path)


@contextmanager
def single_writer(run):
    lock = run/'.writer.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd,str(os.getpid()).encode()); os.close(fd)
        yield
    finally:
        lock.unlink()


def safe_api_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname != 'api.github.com' or parsed.port not in (None,443) or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('GET destination outside public GitHub API boundary')
    if not parsed.path.startswith(('/repos/','/repositories/')) or any(x in ('.','..') for x in urllib.parse.unquote(parsed.path).split('/')):
        raise ValueError('GET path outside repository endpoint boundary')
    if set(urllib.parse.parse_qs(parsed.query,keep_blank_values=True))-{'ref'}:
        raise ValueError('Unexpected query parameter; credentials and arbitrary query strings are forbidden')
    return url


def clean_excerpt(text):
    text = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16})\b','[REDACTED]',text)
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[EMAIL REDACTED]',text)
    text = re.sub(r'''(?i)(?:[A-Z]:[\\/](?:Users|Documents and Settings)[\\/]|/(?:Users|home)/)[^\s<>"')\]]+''','[LOCAL PATH REDACTED]',text)
    return text[:16000]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHubTransport:
    """GET only; no token, environment credential or arbitrary endpoint fallback."""
    def __init__(self):
        self.opener = urllib.request.build_opener(NoRedirect())

    def __call__(self, url, timeout, max_bytes):
        request = urllib.request.Request(safe_api_url(url), method='GET', headers={
            'Accept':'application/vnd.github+json','X-GitHub-Api-Version':API_VERSION,
            'User-Agent':'myAI-StackGuide-catalog-refresh'})
        try:
            response = self.opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            return error.code, dict(error.headers), b''
        with response:
            body = response.read(max_bytes+1)
            return response.status, dict(response.headers), body


def create_plan(run, source, taxonomy, contract, max_requests=30, max_repos=1):
    if max_requests < 1 or max_repos < 1:
        raise ValueError('Budgets must be positive')
    run.mkdir(parents=True,exist_ok=False)
    paths={'input.json':Path(source),'taxonomy.json':Path(taxonomy),'field-contract.json':Path(contract)}
    pins={}
    for name,path in paths.items():
        (run/name).write_bytes(path.read_bytes())
        pins[name]={'sha256':sha(path),'origin':str(path.resolve())}
    data=load(run/'input.json')
    def priority(r):
        stars=r.get('stars')
        return 0 if stars==0 else 1 if isinstance(stars,int) and 0<stars<500 else 2
    queue=[r['id'] for r in sorted(data['repositories'],key=priority)]
    plan={'version':'1.0.0','createdAt':now(),'pins':pins,'queue':queue,'collectorSha256':sha(__file__),
          'apiVersion':API_VERSION,'maxRequests':max_requests,'maxReposPerInvocation':max_repos,
          'maxBytes':8_000_000,'maxResponseBytes':1_000_000,'timeoutSeconds':15,'maxRetries':2,
          'maxRedirects':3,'maxManifests':4,'maxSecondsPerInvocation':300,
          'scope':'public_GET_only_no_credentials_no_canonical_write'}
    atomic_json(run/'plan.json',plan)
    atomic_json(run/'checkpoint.json',{'requests':0,'bytes':0,'retryNotBefore':0,'identities':{},'records':{}})
    return plan


class Collector:
    def __init__(self, run, transport=None):
        self.run=Path(run); self.plan=load(self.run/'plan.json'); self.state=load(self.run/'checkpoint.json')
        self.transport=transport or GitHubTransport()
        self.validate_url=getattr(self.transport, 'validate_url', safe_api_url)
        self.started=time.monotonic()
        self.check_pins()
        self.contract=load(self.run/'field-contract.json')
        policy=self.contract['eligibility_policy']
        if policy.get('max_low_star_exceptions') != 0 or policy.get('default_min_stars') != 500:
            raise ValueError('The active owner policy requires a strict 500-Star minimum; migrate the field contract explicitly')
        self.min_stars=policy['default_min_stars']
        self.taxonomy=load(self.run/'taxonomy.json')
        self.source={r['id']:r for r in load(self.run/'input.json')['repositories']}

    def check_pins(self):
        if self.plan.get('collectorSha256')!=sha(__file__):
            raise ValueError('Collector changed; explicit migration or a new run is required')
        for name,pin in self.plan['pins'].items():
            if sha(self.run/name)!=pin['sha256'] or sha(pin['origin'])!=pin['sha256']:
                raise ValueError('Input/contract changed; explicit migration or a new run is required')

    def save_state(self):
        atomic_json(self.run/'checkpoint.json',self.state)

    def trace(self,event):
        with (self.run/'request-log.jsonl').open('a',encoding='utf-8') as handle:
            handle.write(json.dumps(event,ensure_ascii=False)+'\n');handle.flush();os.fsync(handle.fileno())

    def record_path(self, record_id):
        return self.run/'records'/(hashlib.sha256(record_id.encode()).hexdigest()+'.json')

    def request(self,url):
        retry=0; redirects=0
        while True:
            self.validate_url(url)
            if self.state.get('haltReason'):
                return {'status':'fetch_error','reason':self.state['haltReason'],'url':url,'observedAt':now()}
            if time.time()<self.state['retryNotBefore']:
                return {'status':'budget_exhausted','reason':'rate_limit_wait','url':url,'observedAt':now()}
            if self.state['requests']>=self.plan['maxRequests'] or self.state['bytes']>=self.plan['maxBytes'] or time.monotonic()-self.started>=self.plan['maxSecondsPerInvocation']:
                return {'status':'budget_exhausted','reason':'run_budget','url':url,'observedAt':now()}
            self.state['requests']+=1;self.save_state()  # Debit before I/O, including failures/redirects.
            self.trace({'attempt':self.state['requests'],'phase':'start','method':'GET','url':url,'at':now()})
            remaining=min(self.plan['maxResponseBytes'],self.plan['maxBytes']-self.state['bytes'])
            try:
                code,headers,body=self.transport(url,self.plan['timeoutSeconds'],remaining)
            except (urllib.error.URLError,TimeoutError,OSError):
                code,headers,body=599,{},b''
            header={k.lower():v for k,v in headers.items()}
            rate={key:header[key] for key in ('x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-used','x-ratelimit-reset','x-ratelimit-resource','retry-after') if key in header}
            self.state['bytes']+=len(body)
            if rate:self.state['lastRateLimit']={**rate,'observedAt':now()}
            self.save_state()
            self.trace({'attempt':self.state['requests'],'phase':'finish','httpStatus':code,'bytes':len(body),'rateLimit':rate,'at':now()})
            if len(body)>remaining:
                return {'status':'budget_exhausted','reason':'response_size','url':url,'observedAt':now()}
            if code in (301,302,303,307,308):
                redirects+=1
                if redirects>self.plan['maxRedirects']:
                    return {'status':'fetch_error','reason':'redirect_limit','url':url,'observedAt':now()}
                try:url=self.validate_url(urllib.parse.urljoin(url,header.get('location','')))
                except ValueError:return {'status':'fetch_error','reason':'unsafe_redirect','url':url,'observedAt':now()}
                continue
            if code == 401:
                self.state['haltReason']='authentication_failed';self.save_state()
                return {'status':'fetch_error','reason':'authentication_failed','httpStatus':code,'url':url,'observedAt':now()}
            try:error_message=json.loads(body).get('message','').lower() if code>=400 and body else ''
            except (ValueError,AttributeError):error_message=''
            rate_limited=code==429 or (code==403 and (header.get('x-ratelimit-remaining')=='0' or 'retry-after' in header or 'rate limit' in error_message or 'abuse' in error_message))
            if rate_limited:
                try:delay=max(60,int(header.get('retry-after',60)),int(header.get('x-ratelimit-reset',0))-int(time.time()))
                except (ValueError,TypeError):delay=60
                self.state['retryNotBefore']=time.time()+delay;self.save_state()
                return {'status':'fetch_error','reason':'rate_limited','httpStatus':code,'url':url,'observedAt':now()}
            if code==403:
                return {'status':'fetch_error','reason':'permission_denied','httpStatus':code,'url':url,'observedAt':now()}
            if code>=500 and retry<self.plan['maxRetries']:
                time.sleep(2**retry);retry+=1;continue
            if code in (404,409):
                return {'status':'source_absent','httpStatus':code,'url':url,'observedAt':now()}
            if code!=200:
                return {'status':'fetch_error','reason':'http_error','httpStatus':code,'url':url,'observedAt':now()}
            if header.get('x-ratelimit-remaining')=='0':
                try:self.state['retryNotBefore']=max(time.time()+60,float(header.get('x-ratelimit-reset',0)))
                except (ValueError,TypeError):self.state['retryNotBefore']=time.time()+60
                self.save_state()
            try:value=json.loads(body)
            except (ValueError,UnicodeError):
                return {'status':'fetch_error','reason':'invalid_json','url':url,'observedAt':now()}
            return {'status':'observed','data':value,'url':url,'observedAt':now()}

    def block(self,record,key,url,project):
        previous=record['blocks'].get(key)
        if previous and previous['status'] in ('observed','source_absent'):
            return previous
        result=self.request(url)
        if result['status']=='observed':
            try:result['data']=project(result['data'])
            except (ValueError,TypeError,KeyError,AttributeError):
                result={k:v for k,v in result.items() if k!='data'}
                result.update(status='fetch_error',reason='invalid_or_unsafe_source_shape')
        if previous:
            record.setdefault('blockHistory',[]).append({k:v for k,v in previous.items() if k!='data'})
        record['blocks'][key]=result
        atomic_json(self.record_path(record['sourceId']),record)
        return result

    def process(self,record_id,curation=None,*,blocks=None):
        # A selective run requests only needed groups; metadata gates public access.
        wanted=lambda key: blocks is None or key in blocks
        source=self.source[record_id];name=source['fullName']
        if not NAME.fullmatch(name):raise ValueError('Invalid repository name')
        path=self.record_path(record_id)
        record=load(path) if path.exists() else {'sourceId':record_id,'blocks':{}}

        def meta(raw):
            if raw.get('private') is not False or raw.get('visibility')!='public' or not NAME.fullmatch(raw.get('full_name','')):
                raise ValueError('Only positively public repositories may be persisted')
            if raw.get('html_url','').casefold()!='https://github.com/'+raw['full_name'].casefold():raise ValueError('Invalid canonical URL')
            if not isinstance(raw.get('id'),int) or isinstance(raw['id'],bool) or raw['id']<=0:raise ValueError('Invalid GitHub numeric identity')
            result={target:raw.get(key) for target,key in FACTS.items()}
            license=raw.get('license') or {}
            result.update({'license.spdx':license.get('spdx_id'),'license.name':license.get('name'),'license.source':license.get('url')})
            return result

        metadata=self.block(record,'metadata',API+'/repos/'+name,meta)
        if metadata['status']=='observed':
            facts=metadata['data'];name=facts['fullName'];base=API+'/repos/'+name
            identity=facts.get('githubRepositoryId')
            conflict=source.get('githubRepositoryId') not in (None,identity)
            other=self.state['identities'].get(str(identity)) if isinstance(identity,int) and not isinstance(identity,bool) else None
            if other and other!=record_id and not conflict:
                record['aliasOf']=other
                record['status']='verified_identity_alias'
                atomic_json(path,record);self.state['records'][record_id]=record['status'];self.save_state()
                return record
            if isinstance(identity,int) and not isinstance(identity,bool) and not conflict:
                self.state['identities'][str(identity)]=record_id;self.save_state()
            stars=facts.get('stars')
            if isinstance(stars,int) and not isinstance(stars,bool) and 0 <= stars < self.min_stars:
                # Confirmed rejection needs no additional content/API work.
                record=self.normalize(record,source,curation or record.get('curation'))
                atomic_json(path,record)
                self.state['records'][record_id]=record['status'];self.save_state()
                return record
            branch=facts.get('defaultBranch')
            if wanted('languages'):
                self.block(record,'languages',base+'/languages',lambda x:{k:v for k,v in x.items() if isinstance(v,int) and not isinstance(v,bool) and v>=0})
            if isinstance(branch,str) and branch and any(wanted(k) for k in ('head_commit','readme','manifests')):
                def commit(x):return {'sha':x['sha'],'date':x['commit']['committer']['date'],'branch':branch}
                head=self.block(record,'head_commit',base+'/commits/'+urllib.parse.quote(branch,safe=''),commit)
                if head['status']=='observed':
                    ref=head['data']['sha']
                    query='?ref='+urllib.parse.quote(ref,safe='')
                    def content(x):
                        if x.get('type')!='file' or x.get('encoding')!='base64':raise ValueError('Not an ordinary base64 file')
                        raw=base64.b64decode(x['content']);return {'path':x['path'],'sha':x['sha'],'ref':ref,'excerpt':clean_excerpt(raw.decode('utf-8')),'truncated':len(raw)>16000}
                    if wanted('readme'):
                        self.block(record,'readme',base+'/readme'+query,content)
                    def root_entries(x):
                        if not isinstance(x,list):raise ValueError('Expected root directory')
                        return sorted(e['name'] for e in x if e.get('type')=='file' and e.get('name') in MANIFEST_NAMES)
                    if wanted('manifests'):
                        listing=self.block(record,'manifest_names',base+'/contents'+query,root_entries)
                        for filename in listing.get('data',[])[:self.plan['maxManifests']]:
                            self.block(record,'file:'+filename,base+'/contents/'+urllib.parse.quote(filename,safe='')+query,content)
                        record['manifestEvidenceTruncated']=len(listing.get('data',[]))>self.plan['maxManifests']
            if wanted('release'):
                self.block(record,'release',base+'/releases/latest',lambda x:{'publishedAt':x.get('published_at'),'tag':x.get('tag_name')})
        record=self.normalize(record,source,curation or record.get('curation'))
        atomic_json(path,record)
        self.state['records'][record_id]=record['status'];self.save_state()
        return record

    def normalize(self,record,source,curation):
        definitions={f['id']:f for f in self.contract['fields']}
        values={};observations={key:{'field':key,'status':'not_attempted','reason':'not_collected_or_not_reviewed'} for key in definitions}
        def set_value(key,value,status,refs):
            values[key]=value
            timestamps=[record['blocks'][ref]['observedAt'] for ref in refs if ref in record['blocks']]
            observations[key]={'field':key,'status':status if value is not None else 'source_absent','evidenceRefs':refs,
                               'observedAt':timestamps[0] if timestamps else self.plan['createdAt']}
        for key,value in {'id':source['id'],'sourceRecordIds':[source['id']],'catalogStatus':source['catalogStatus']}.items():
            set_value(key,value,'observed',['frozen_input'])
        meta=record['blocks'].get('metadata',{})
        if meta.get('status')=='observed':
            for key,value in meta['data'].items():set_value(key,value,'observed',['metadata'])
            full=values['fullName'];identity=values.get('githubRepositoryId')
            conflict=source.get('githubRepositoryId') not in (None,identity)
            set_value('aliases',[source['fullName']] if full.casefold()!=source['fullName'].casefold() else [],'derived_reviewed',['metadata'])
            set_value('identityStatus','conflict' if conflict else 'resolved','derived_reviewed',['metadata'])
            set_value('availability','available','observed',['metadata'])
            set_value('watchersScope','subscribers_count','derived_reviewed',['metadata'])
            set_value('license.confidence','source_reported' if values.get('license.spdx') else None,'derived_reviewed',['metadata'])
            description=values.get('description')
            if isinstance(description,str) and description.strip():
                set_value('catalogDescription',description,'observed',['metadata'])
                set_value('descriptionOrigin','upstream','derived_reviewed',['metadata'])
            set_value('activity.observedAt',meta['observedAt'],'observed',['metadata'])
        elif meta.get('status')=='source_absent':
            set_value('availability','unavailable_public_endpoint','observed',['metadata'])
        else:
            for key in FACTS:observations[key]={'field':key,'status':meta.get('status','not_attempted'),'reason':meta.get('reason','metadata_unavailable')}
        for block,mapping in [('languages',{'languages':None}),('head_commit',{'activity.lastCommitAt':'date','activity.lastCommitSha':'sha','activity.lastCommitBranch':'branch'}),('release',{'activity.lastReleaseAt':'publishedAt'})]:
            item=record['blocks'].get(block,{})
            for field,key in mapping.items():
                if item.get('status')=='observed':set_value(field,item['data'] if key is None else item['data'].get(key),'observed',[block])
                elif item:observations[field]={'field':field,'status':item['status'],'evidenceRefs':[block]}
        permitted={f['id'] for f in definitions.values() if f['source'].startswith('curator:')}|{'descriptionOrigin'}
        if curation:
            if curation.get('sourceId')!=source['id']:raise ValueError('Curation identity mismatch')
            for key,value in curation.get('fields',{}).items():
                refs=curation.get('evidenceRefs',{}).get(key,[])
                if key not in permitted or not refs or any(record['blocks'].get(ref,{}).get('status')!='observed' for ref in refs):raise ValueError('Curation requires an allowed field and successful source blocks')
                set_value(key,value,'derived_reviewed',refs)
        leaves={n['id'] for n in self.taxonomy['categories'] if n['kind']=='category'}
        category=values.get('primaryCategory')
        if category is not None and category not in leaves:raise ValueError('Invalid primary category: container, retired or review ID')
        secondary=values.get('secondaryCategories',[])
        if not isinstance(secondary,list) or len(secondary)!=len(set(secondary)) or category in secondary or any(c not in leaves for c in secondary):raise ValueError('Invalid secondary categories')
        if values.get('descriptionOrigin')=='upstream' and values.get('catalogDescription')!=values.get('description'):raise ValueError('Derived text cannot claim upstream origin')
        if values.get('descriptionOrigin') not in (None,'upstream','curator_summary'):raise ValueError('Unknown description origin')
        if 'stack' in values and (not isinstance(values['stack'],list) or not values['stack'] or any(not isinstance(x,dict) or not x.get('technology') or not x.get('evidenceRefs') or any(record['blocks'].get(ref,{}).get('status')!='observed' for ref in x['evidenceRefs']) for x in values['stack'])):raise ValueError('Stack requires technology evidence')
        set_value('activity.status','metadata_observed' if meta.get('status')=='observed' else 'pending_enrichment','derived_reviewed',['metadata'])
        set_value('provenance',{'inputSha256':self.plan['pins']['input.json']['sha256'],'apiVersion':API_VERSION,'sourceId':source['id']},'derived_reviewed',['frozen_input'])
        # Derived self-reporting fields are assessed after substantive mandatory facts.
        computed={'fieldObservations','evidenceCompleteness','eligibility'}
        missing=[]
        for field in self.contract['mandatory_fields']:
            if field in computed:continue
            value=values.get(field);kind=definitions[field]['value_type']
            valid=observations[field]['status'] in ('observed','derived_reviewed') and value is not None
            if kind in ('string','enum','timestamp'):valid=valid and isinstance(value,str) and bool(value.strip()) and value not in {'unknown','Not available'}
            if kind=='integer':valid=valid and isinstance(value,int) and not isinstance(value,bool) and value>=0
            if kind=='boolean':valid=valid and isinstance(value,bool)
            if kind.startswith('array['):valid=valid and isinstance(value,list)
            if kind=='timestamp':
                try:datetime.fromisoformat(value.replace('Z','+00:00'))
                except (ValueError,AttributeError,TypeError):valid=False
            if not valid:missing.append(field)
        if values.get('reviewStatus') not in {'reviewed','curator_reviewed'} and 'reviewStatus' not in missing:missing.append('reviewStatus')
        reasons=[]
        stars=values.get('stars')
        if not isinstance(stars,int) or isinstance(stars,bool):reasons.append('stars_unknown')
        elif stars==0:reasons.append('confirmed_zero_stars')
        elif stars<0:reasons.append('stars_invalid')
        elif stars<self.min_stars:reasons.append('confirmed_below_minimum_stars')
        if values.get('identityStatus')!='resolved':reasons.append('identity_unresolved')
        if values.get('availability')!='available':reasons.append('availability_unresolved')
        if missing:reasons.append('mandatory_fields_unresolved')
        set_value('evidenceCompleteness',round(100*(len(self.contract['mandatory_fields'])-len(missing))/len(self.contract['mandatory_fields']),2),'derived_reviewed',['field_contract'])
        excluded=isinstance(stars,int) and not isinstance(stars,bool) and 0 <= stars < self.min_stars
        set_value('eligibility',{'dataGatePassed':not reasons,'reasons':reasons,'minimumStars':self.min_stars,'replacementRequired':excluded,'catalogAcceptanceChanged':False,'globalCAT07Applied':False},'derived_reviewed',['field_contract'])
        observations['fieldObservations']={'field':'fieldObservations','status':'derived_reviewed','evidenceRefs':['blocks']}
        values['fieldObservations']=list(observations.values())
        status='excluded_below_star_threshold' if excluded else 'complete_card' if not missing and not reasons else 'needs_review_or_retry'
        record.update(values=values,missingMandatory=missing,status=status)
        if curation:record['curation']=curation
        return record

    def execute(self,curation_dir=None,repository=None):
        attempted=0
        if repository is not None and repository not in self.plan['queue']:
            raise ValueError('Selected repository is not in the frozen queue')
        queue=[repository] if repository is not None else self.plan['queue']
        for record_id in queue:
            if attempted>=self.plan['maxReposPerInvocation']:break
            if self.state['records'].get(record_id) in ('complete_card','verified_identity_alias','excluded_below_star_threshold'):continue
            curation=None
            if curation_dir:
                path=Path(curation_dir)/self.record_path(record_id).name
                if path.exists():curation=load(path)
            existing=self.record_path(record_id)
            if existing.exists() and not curation:
                saved=load(existing)
                if saved.get('values') and not any(b['status'] in ('fetch_error','budget_exhausted') for b in saved['blocks'].values()):
                    # A pending curator card must not starve the next untouched repository.
                    continue
            self.process(record_id,curation);attempted+=1
            if time.time()<self.state['retryNotBefore'] or self.state['requests']>=self.plan['maxRequests']:break
        return {'attempted':attempted,'requests':self.state['requests'],'bytes':self.state['bytes'],'retryNotBefore':self.state['retryNotBefore'],'records':self.state['records']}

    def verify(self):
        self.check_pins()
        for record_id in self.state['records']:
            record=load(self.record_path(record_id))
            if record['sourceId']!=record_id:raise ValueError('Record identity drift')
            if record.get('aliasOf'):
                if record['aliasOf'] not in self.source:raise ValueError('Alias target missing')
                target=load(self.record_path(record['aliasOf']))
                if record['blocks']['metadata']['data']['githubRepositoryId']!=target['blocks']['metadata']['data']['githubRepositoryId']:raise ValueError('Alias numeric identity mismatch')
                continue
            if len(record['values']['fieldObservations'])!=len(self.contract['fields']):raise ValueError('Incomplete observation coverage')
            prior=json.dumps([record['values'],record['missingMandatory'],record['status']],sort_keys=True)
            recomputed=self.normalize(record,self.source[record_id],record.get('curation'))
            if prior!=json.dumps([recomputed['values'],recomputed['missingMandatory'],recomputed['status']],sort_keys=True):raise ValueError('Normalized card differs from stored source blocks or curator evidence')
        return {'verifiedRecords':len(self.state['records']),'networkPerformed':False,'scope':'local_checkpoint_consistency_only'}

    def build(self):
        result=self.verify()
        records=[load(self.record_path(i)) for i in self.state['records']]
        excluded=[r for r in records if r['status']=='excluded_below_star_threshold']
        atomic_json(self.run/'excluded-records.json',{'scope':'audit_history_not_active_catalog','records':excluded})
        replacements=[{'excludedSourceId':r['sourceId'],'fullName':r['values']['fullName'],
                       'observedStars':r['values']['stars'],'metadataObservedAt':r['blocks']['metadata']['observedAt'],
                       'minimumStars':self.min_stars,'status':'replacement_search_required'} for r in excluded]
        resolutions_path=self.run/'replacement-resolutions.json'
        resolutions=load(resolutions_path) if resolutions_path.exists() else {}
        for item in replacements:
            replacement_id=resolutions.get(item['excludedSourceId'])
            if replacement_id:
                if self.state['records'].get(replacement_id)!='complete_card':
                    raise ValueError('Replacement must be a verified complete card')
                if self.source[replacement_id].get('discovery',{}).get('replacementFor')!=item['excludedSourceId']:
                    raise ValueError('Replacement must be explicitly registered for this excluded identity')
                item.update(status='qualified_replacement_found',replacementSourceId=replacement_id)
        atomic_json(self.run/'replacement-queue.json',{'items':replacements})
        cards=[r for r in records if r['status']=='complete_card']
        pending=[r for r in records if r['status']=='needs_review_or_retry']
        atomic_json(self.run/'candidate-cards.json',{'scope':'data_complete_candidates_not_catalog_acceptance','cards':cards,'pendingCards':pending})
        return {**result,'output':'candidate-cards.json','completeCards':len(cards),'excludedRecords':len(excluded),'pendingCards':len(pending)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['plan','run','resume','verify','build'])
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--input',type=Path,default=ROOT/'data/catalog_manifest.json')
    parser.add_argument('--taxonomy',type=Path,default=ROOT/'specs/catalog/taxonomy.yaml')
    parser.add_argument('--field-contract',type=Path,default=ROOT/'specs/catalog/enrichment-field-contract.json')
    parser.add_argument('--max-requests',type=int,default=30)
    parser.add_argument('--max-repos',type=int,default=1)
    parser.add_argument('--curation-dir',type=Path)
    parser.add_argument('--repository',help='Exact frozen source ID; restrict run/resume to this record only')
    args=parser.parse_args()
    if args.mode=='plan':result=create_plan(args.run_dir,args.input,args.taxonomy,args.field_contract,args.max_requests,args.max_repos)
    else:
        with single_writer(args.run_dir):
            collector=Collector(args.run_dir)
            if args.mode in ('run','resume'):result=collector.execute(args.curation_dir,args.repository)
            else:
                result=collector.build() if args.mode=='build' else collector.verify()
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    main()
