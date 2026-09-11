#!/usr/bin/env python3
import csv,json,math,requests,urllib3,datetime,pathlib
urllib3.disable_warnings()
BASE='https://50.28.86.131'
FOUNDER=['founder_founders','founder_dev_fund','founder_team_bounty','founder_community']
s=requests.Session(); s.headers['User-Agent']='zaguzovmaksim0-hue-rtc-distribution/1.0'
def get(path,params=None):
 r=s.get(BASE+path,params=params,timeout=20,verify=False); r.raise_for_status(); return r.json()
miners=get('/api/miners',{'limit':1000}).get('miners',[])
epoch=get('/epoch')
ids=[]
for m in miners:
 x=m.get('miner')
 if x and x not in ids:ids.append(x)
# Add the four documented founder wallets so exclusion can be explicit and their balances auditable.
for x in FOUNDER:
 if x not in ids:ids.append(x)
rows=[]
for x in ids:
 try:
  b=get('/wallet/balance',{'miner_id':x}); bal=float(b.get('amount_rtc',0) or 0)
 except Exception as e:
  bal=None
 m=next((z for z in miners if z.get('miner')==x),{})
 rows.append({'wallet':x,'balance_rtc':bal,'founder':x in FOUNDER,'active_miner':bool(m),'device_family':m.get('device_family',''),'device_arch':m.get('device_arch',''),'antiquity_multiplier':m.get('antiquity_multiplier','')})
def gini(vals):
 v=sorted(x for x in vals if x is not None and x>=0); n=len(v)
 if not n or sum(v)==0:return 0.0
 total=sum(v); return (2*sum((i+1)*x for i,x in enumerate(v))/(n*total))-((n+1)/n)
def stats(sub):
 vals=[r['balance_rtc'] for r in sub if r['balance_rtc'] is not None]; positive=[x for x in vals if x>0]; total=sum(vals)
 ranked=sorted(sub,key=lambda r:(r['balance_rtc'] or 0),reverse=True)
 return {'wallets':len(vals),'nonzero':len(positive),'total_rtc':total,'gini':gini(vals),'median':(sorted(vals)[len(vals)//2] if vals else 0),'top1_share':((ranked[0]['balance_rtc'] or 0)/total if total else 0),'top5_share':(sum((r['balance_rtc'] or 0) for r in ranked[:5])/total if total else 0),'top10_share':(sum((r['balance_rtc'] or 0) for r in ranked[:10])/total if total else 0)}
active=[r for r in rows if r['active_miner']]
nonfounder=[r for r in active if not r['founder']]
founders=[r for r in rows if r['founder']]
summary={'snapshot_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'epoch':epoch,'public_scope':'active miners returned by /api/miners?limit=1000 plus four founder wallets named in public tokenomics docs','active_all':stats(active),'active_nonfounder':stats(nonfounder),'founder_wallets':stats(founders),'api_limitations':{'/api/balances':'HTTP 401 admin_required','/api/wallets':'HTTP 404','/api/holders':'HTTP 404','/wallet/rich-list':'HTTP 404'}}
path=pathlib.Path('.')
with open('wallets.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
path.joinpath('summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
# Simple SVG Lorenz curve for active non-founder wallets, including zeros.
vals=sorted(r['balance_rtc'] or 0 for r in nonfounder); total=sum(vals); pts=[(0,0)]; c=0
for i,x in enumerate(vals,1): c+=x; pts.append((i/len(vals),c/total if total else 0))
W=760;H=520;ml=70;mr=30;mt=40;mb=70
coords=' '.join(f'{ml+x*(W-ml-mr):.1f},{H-mb-y*(H-mt-mb):.1f}' for x,y in pts)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><text x="{W/2}" y="25" text-anchor="middle" font-family="sans-serif" font-size="20">RTC active non-founder miner balance Lorenz curve</text><line x1="{ml}" y1="{H-mb}" x2="{W-mr}" y2="{mt}" stroke="#999" stroke-dasharray="6 5"/><polyline points="{coords}" fill="none" stroke="#1769aa" stroke-width="4"/><line x1="{ml}" y1="{mt}" x2="{ml}" y2="{H-mb}" stroke="#222"/><line x1="{ml}" y1="{H-mb}" x2="{W-mr}" y2="{H-mb}" stroke="#222"/><text x="{W/2}" y="{H-20}" text-anchor="middle" font-family="sans-serif">Cumulative share of active-visible wallets</text><text x="20" y="{H/2}" transform="rotate(-90 20 {H/2})" text-anchor="middle" font-family="sans-serif">Cumulative share of RTC balance</text><text x="{ml}" y="{H-mb+25}" font-family="sans-serif">0</text><text x="{W-mr-10}" y="{H-mb+25}" font-family="sans-serif">1</text><text x="{ml-25}" y="{mt+5}" font-family="sans-serif">1</text></svg>'''
path.joinpath('lorenz.svg').write_text(svg)
print(json.dumps(summary,indent=2,ensure_ascii=False))
print('TOP10_NONFOUNDER')
for i,r in enumerate(sorted(nonfounder,key=lambda r:r['balance_rtc'] or 0,reverse=True)[:10],1): print(i,r['wallet'],r['balance_rtc'],r['device_family'],r['antiquity_multiplier'])
