import bpy
import asset_runner as R
def check():
 errors=[];c=bpy.data.collections.get(R.PREFIX+'healthy_LOD0')
 if not c:return {},['healthy composition missing']
 required=['ClayMould','CoreSpindle','FurnaceFace','PouringChannel','FinishedGun','SmallSwivelGun','SwivelPivot','LiftHeader','TackleHook','PulleyWheel','PulleyAxle','PulleyCheek-1','PulleyCheek1','TackleRope','TackleCleat']
 missing=[n for n in required if not bpy.data.objects.get(R.PREFIX+n)]
 if missing:errors.append('missing production anatomy '+str(missing))
 bed=bpy.data.objects.get(R.PREFIX+'CastingBed');rim=bpy.data.objects.get(R.PREFIX+'PitSide1')
 if bed and rim and R.bounds(bed)[1][2]>=R.bounds(rim)[1][2]:errors.append('casting recess lacks depth')
 wheels=[o for o in c.all_objects if o.name.endswith('Tyre')]
 if len(wheels)!=4:errors.append('four carriage wheels required')
 for o in wheels:
  if abs(R.bounds(o)[0][2]-.18)>.001:errors.append('wheel does not meet ground '+o.name)
 hook=bpy.data.objects.get(R.PREFIX+'TackleHook')
 if bed and hook:
  a,b=R.bounds(bed);d,e=R.bounds(hook);xy=[(d[i]+e[i])/2 for i in range(2)]
  if any(xy[i]<a[i] or xy[i]>b[i] for i in range(2)):errors.append('mould-lifting hook is not above the casting bed')
 beam=bpy.data.objects.get(R.PREFIX+'CanopyLongBeam0')
 for o in c.all_objects:
  if 'CanopyOwnerCloth' in o.name and o.name.startswith(R.PREFIX+'CanopyOwnerCloth'):
   if abs(R.bounds(o)[1][0]-R.bounds(beam)[0][0])>.001:errors.append('owner cloth not seated into canopy beam '+o.name)
 for state in [f'damage_{i}' for i in range(1,6)]:
  statecol=bpy.data.collections.get(R.PREFIX+state+'_LOD0')
  if not statecol:continue
  for o in statecol.all_objects:
   src=bpy.data.objects.get(o.get('healthy_source',''))
   if src and 'OwnerCloth' in src.name and abs(R.bounds(o)[1][2]-R.bounds(src)[1][2])>.001:errors.append('damaged cloth lost upper attachment '+o.name)
 return {'production_anatomy_present':not missing,'casting_recess':not errors,'grounded_carriage_wheels':len(wheels)},errors
