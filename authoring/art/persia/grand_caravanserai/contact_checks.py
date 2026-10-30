"""Measure real mesh interface planes and declared tolerances."""
import bpy,json
import asset_runner as R
P=R.PREFIX
def run(final=False):
    rows=[]
    def bounds(n):return R.bounds(bpy.data.objects[P+n])
    def gap(label,value,lo=-.00002,hi=.00002):rows.append({'interface':label,'signed_gap':value,'allowed':[lo,hi],'passed':lo<=value<=hi})
    for side in [-1,1]:
        label='West' if side<0 else 'East'
        for j in range(4):
            for ss in [-1,1]:
                b=bounds(label+'Bay'+str(j)+'_Bearing'+str(ss));v=bounds(label+'Bay'+str(j)+'_Vault');f=bounds(label+'Platform')
                gap(label+str(j)+' bearing'+str(ss)+'/platform',b[0][2]-f[1][2])
                gap(label+str(j)+' vault/bearing'+str(ss),v[0][2]-b[1][2])
            v=bounds(label+'Bay'+str(j)+'_Vault');a=bounds(label+'Bay'+str(j)+'_Facade');outer=bounds(label+'OuterWall')
            gap(label+str(j)+' front cap/vault',a[0 if side<0 else 1][0]-v[1 if side<0 else 0][0])
            gap(label+str(j)+' vault/rear enclosure',side*(outer[0 if side>0 else 1][0]-v[1 if side>0 else 0][0]),-.101,-.099)
        r=bounds('GateReturn'+str(side));v=bounds('GateVault');gap('Gate vault on return'+str(side),v[0][2]-r[1][2])
        gap('Gate return on plinth'+str(side),r[0][2]-.20)
        rr=bounds('RearIwanReturn'+str(side));vv=bounds('RearIwanVault');gap('Rear iwan vault on return'+str(side),vv[0][2]-rr[1][2])
        vv=bounds('RearRoomVault'+str(side))
        for label in ['RearRoomBearing','RearRoomInnerBearing']:
            bb=bounds(label+str(side));gap(label+str(side)+' spring seat',vv[0][2]-bb[1][2]);gap(label+str(side)+' on rear platform',bb[0][2]-.38)
        inner=bounds('RearRoomInnerBearing'+str(side));gap('Rear inner bearing longitudinal ends'+str(side),vv[0][1]-inner[0][1]);gap('Rear inner bearing rear end'+str(side),inner[1][1]-vv[1][1])
    gap('Gate front cap/vault',bounds('GateVault')[0][1]-bounds('GateFacade')[1][1])
    gap('Gate vault/inner tympanum overlap',bounds('GateInnerTympanum')[0][1]-bounds('GateVault')[1][1],-.201,-.199)
    gap('Rear iwan cap/vault',bounds('RearIwanVault')[0][1]-bounds('RearIwanFront')[1][1])
    gap('Rear iwan/outer wall',bounds('RearOuterWall')[0][1]-bounds('RearIwanVault')[1][1])
    if final:
        for y in [-2.75,-.55]:
            rafter=bpy.data.objects[P+'UnloadingRafter'+str(y)];ends=[sum((v.co[i] for v in list(rafter.data.vertices)[:4]))/4 for i in range(3)]
            gap('Awning rear rafter/post'+str(y),ends[2]-bounds('UnloadingRearPost'+str(y))[1][2])
            gap('Awning rear post/ground'+str(y),bounds('UnloadingRearPost'+str(y))[0][2]-.20)
            gap('Awning front post/ground'+str(y),bounds('UnloadingPost'+str(y))[0][2]-.20)
        for j in range(3):
            b=bounds('UnloadingCrate'+str(j)+'_Body')
            gap('Unloading crate'+str(j)+' ground/stack',b[0][2]-(.20 if j<2 else .68))
        for j in range(4):gap('Jar'+str(j)+' on ground',bounds('WaterJar'+str(j))[0][2]-.20)
        top=bounds('TallyTop')
        for x in [-1.03,-.17]:
            for y in [2.85,3.25]:gap('Tally leg/table'+str(x)+str(y),top[0][2]-bounds('TallyLeg'+str(x)+str(y))[1][2])
        gap('Ledger on tally table',bounds('TallyLedger')[0][2]-top[1][2])
        gap('Trough walls on base',bounds('TroughLong2.2')[0][2]-bounds('TroughBase')[1][2],-.011,-.009)
        for j in range(3):gap('Carpet roll'+str(j)+' on ground',bounds('CarpetRoll'+str(j))[0][2]-.20)
        for y in [-3.82,-3.02]:gap('Cart wheel/ground'+str(y),bounds('CartWheel'+str(y))[0][2]-.20)
        for o in bpy.data.collections[P+'healthy_LOD0'].all_objects:
            if 'Paving_' in o.name:gap('Paver earth bedding '+o.name,R.bounds(o)[0][2]-.20,-.00501,-.00499)
        for o in bpy.data.collections[P+'healthy_LOD0'].all_objects:
            if 'DirtZone' in o.name and abs(sum(v.co.x for v in o.data.vertices)/len(o.data.vertices))>1.3:gap('Operational dirt/soil '+o.name,R.bounds(o)[0][2]-.20,-.00101,-.00099)
    result={'passed':all(x['passed'] for x in rows),'checks':rows,'final_props_included':final,'native_clearance':'deferred'}
    (R.ROOT/'evidence/contact-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print('CONTACTS',len(rows),'FAILURES',[x for x in rows if not x['passed']]);return result
