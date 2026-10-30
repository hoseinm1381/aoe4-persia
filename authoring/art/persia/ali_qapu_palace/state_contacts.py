"""Re-audit defined bearings in each LOD0 lifecycle composition."""
import bpy,json
import asset_runner as R
def run():
 pairs=json.loads((R.ROOT/'anchors.json').read_text())['contacts'];rows=[];errors=[]
 for state in ['healthy']+[f'damage_{i}' for i in range(1,6)]+['ruins']:
  c=bpy.data.collections.get(R.PREFIX+state+'_LOD0')
  if not c:errors.append('missing '+state);continue
  obs={o.get('healthy_source',o.name):o for o in c.all_objects if o.type=='MESH'}
  for p in pairs:
   lo=obs.get(R.PREFIX+p['lower']);hi=obs.get(R.PREFIX+p['upper'])
   if hi is None:continue # The upper component was deliberately destroyed.
   if lo is None:errors.append(state+': missing support '+p['lower']+' for '+p['upper']);continue
   a,b=R.bounds(lo);d,e=R.bounds(hi);axis=p.get('axis',2);gap=d[axis]-b[axis]
   overlap=[min(b[i],e[i])-max(a[i],d[i]) for i in range(3) if i!=axis]
   passed=-.25<=gap<=p.get('tolerance',.015) and min(overlap)>=-.001
   row={'state':state,'interface':p['name'],'signed_gap':gap,'horizontal_overlap':overlap,'passed':passed};rows.append(row)
   if not passed:errors.append(state+': '+p['name'])
 result={'passed':not errors,'checked':len(rows),'interfaces':rows,'errors':errors,'scope':'Defined authored LOD0 bearing planes in every surviving lifecycle pair; LOD topology/bounds and reference views checked separately. Not engine collision.'}
 (R.ROOT/'evidence/state-contact-checks.json').write_text(json.dumps(result,indent=2)+'\n');print('STATE_CONTACTS',result['passed'],len(rows),errors[:6]);return result
