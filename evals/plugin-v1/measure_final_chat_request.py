import argparse,ctypes,hashlib,json,math,platform,statistics,subprocess,sys,time
from ctypes import wintypes
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'plugins/myai-stackguide/scripts'))
import recommendation_request as runtime
OUT=ROOT/'evals/plugin-v1/results/cp04-final-chat-resource-2026-10-11/resource-check.json'
CASES=ROOT/'evals/plugin-v1/results/cp04-final-quality-prospective-2026-10-11/observations.json'
def sample():
 row=next(r for r in json.loads(CASES.read_bytes())['records'] if r['case_id']=='PROSPECTIVE-HOLD-07')['payload']
 t=time.perf_counter()
 request=runtime.prepare_from_brief(row['brief'],row['interpretation']);q=request['catalog_query']
 prepared=time.perf_counter();r=runtime.retrieval.retrieve(q,run_id=row['brief']['run_id'],index_path=runtime.ASSETS/'catalog.search.sqlite',manifest_path=runtime.ASSETS/'catalog.search-manifest.json',policy_path=runtime.ASSETS/'retrieval-policy.json')
 return {'ms':(time.perf_counter()-t)*1000,'prepare_count_ms':(prepared-t)*1000,'c9_ms':(time.perf_counter()-prepared)*1000,'status':r['status'],'query_sha256':runtime.digest(q),'query_derivation':request['query_derivation']}
class Memory(ctypes.Structure):
 _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(k,ctypes.c_size_t) for k in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
def peak():
 v=Memory();v.cb=ctypes.sizeof(v)
 get=ctypes.windll.kernel32.GetCurrentProcess;get.restype=wintypes.HANDLE
 memory=ctypes.windll.psapi.GetProcessMemoryInfo
 memory.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD];memory.restype=wintypes.BOOL
 if not memory(get(),ctypes.byref(v),v.cb):raise OSError('GetProcessMemoryInfo failed')
 return v.PeakWorkingSetSize
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cold-sample',action='store_true');a=p.parse_args()
 if a.cold_sample:
  v=sample();v['peak_working_set_bytes']=peak();print(json.dumps(v));raise SystemExit(0)
 if OUT.exists():raise ValueError('preserve prior measurement')
 cold=[]
 for _ in range(30):
  r=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--cold-sample'],capture_output=True,text=True,check=True,cwd=ROOT)
  cold.append(json.loads(r.stdout.strip()))
 sample();warm=[sample() for _ in range(30)]
 row=next(r for r in json.loads(CASES.read_bytes())['records'] if r['case_id']=='PROSPECTIVE-HOLD-07')['payload']; start=time.perf_counter(); full=runtime.run(row['brief'],row['interpretation'],row['public_observations']); previous={'ms':(time.perf_counter()-start)*1000,'status':full['status'],'scope':'One warm Brief/COUNT/C9/guard/pack diagnostic; no model or SLA'}
 limits=json.loads((ROOT/'evals/plugin-v1/quality-plan.json').read_bytes())['thresholds']
 p95=lambda xs:sorted(x['ms'] for x in xs)[math.ceil(.95*len(xs))-1]
 v={'scope':'Underfilled chat case: prepared Brief plus COUNT, pinned route metadata, required atoms and leaf terms and final C9 retrieval; guard/pack one separate diagnostic. Existing C9 ceilings applied conservatively to this larger timed seam; no end-to-end/model SLA','python':platform.python_version(),'platform':platform.platform(),'processor':platform.processor(),'cold_definition':'30 new read-only processes/connections; OS cache not flushed, process launch excluded','warm_definition':'same process/immutable index after one discarded warmup','cold_samples':cold,'warm_samples':warm,'cold_p95_ms':p95(cold),'warm_p95_ms':p95(warm),'peak_memory_bytes':max(x['peak_working_set_bytes'] for x in cold),'index_bytes':(runtime.ASSETS/'catalog.search.sqlite').stat().st_size,'prior_whole_path_diagnostic':previous,'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(runtime.__file__),Path(runtime.retrieval.__file__),CASES,runtime.ASSETS/'catalog.search.sqlite',runtime.ASSETS/'catalog.search-manifest.json',runtime.ASSETS/'retrieval-policy.json')},'promotion_ready':False}
 v['gates']={'cold_p95':v['cold_p95_ms']<=limits['actual_cold_p95_ms_max'],'warm_p95':v['warm_p95_ms']<=limits['actual_warm_p95_ms_max'],'peak_memory':v['peak_memory_bytes']<=limits['peak_memory_bytes_max'],'index_bytes':v['index_bytes']<=limits['index_bytes_max'],'statuses':all(x['status']=='ok' for x in cold+warm)}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v[k] for k in ('cold_p95_ms','warm_p95_ms','peak_memory_bytes','index_bytes','gates')}))
