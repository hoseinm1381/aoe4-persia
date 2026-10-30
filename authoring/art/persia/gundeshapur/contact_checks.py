"""Independent measured interfaces, recorded from live mesh bounds."""
import bpy,json
import asset_runner as R

def run():
    rows=[];P=R.PREFIX
    def ob(n):return bpy.data.objects[P+n]
    def plane(label,a,b,axis,fa=1,fb=0,min_gap=-.04,max_gap=.02):
        va=R.bounds(ob(a))[fa][axis];vb=R.bounds(ob(b))[fb][axis];gap=vb-va
        rows.append({'interface':label,'a':a,'b':b,'axis':axis,'signed_gap':gap,'allowed':[min_gap,max_gap],'passed':min_gap-1e-6<=gap<=max_gap+1e-6})
    for side in ('West','East'):
        plane(side+' outer wall to barrel vault',side+'WingOuterWall',side+'WingVault',2)
        plane(side+' main hall wall to roof','Hall'+side+'Wall','HallVault',2)
        plane(side+' side wall to rear wall','Hall'+side+'Wall','HallRearDoor',1,max_gap=.001,min_gap=-.001)
        plane(side+' iwan owner panel bearing',side+'IwanOwnerPanel','IwanFacade',1,max_gap=.001,min_gap=-.001)
    plane('rear chamber carries drum','DomeChamber','DomeDrum',2,max_gap=.001,min_gap=-.001)
    plane('dome lower ring seated in drum','DomeDrum','ReadingDome',2,max_gap=.001,min_gap=-.02)
    a,b=R.bounds(ob('DomeChamber')),R.bounds(ob('DomeDrum'))
    rows.append({'interface':'full drum footprint within chamber bearing','margin_x':min(b[0][0]-a[0][0],a[1][0]-b[1][0]),'margin_y':min(b[0][1]-a[0][1],a[1][1]-b[1][1]),'passed':all(a[0][i]<=b[0][i] and a[1][i]>=b[1][i] for i in (0,1))})
    for j in range(4):plane('document bundle seated on desk '+str(j),'ScribesDesk','DocumentBundle'+str(j),2,max_gap=.001,min_gap=-.001)
    plane('ink pot seated on desk','ScribesDesk','InkPot',2,max_gap=.001,min_gap=-.001)
    plane('writing reed seated on desk','ScribesDesk','WritingReed',2,max_gap=.001,min_gap=-.001)
    plane('stacked entry supply crate','SupplyCrate0','SupplyCrate2',2,max_gap=.001,min_gap=-.001)
    # Rack and freestanding activity props intentionally settle into paving/floor by <= 10 cm.
    for name in ('DocumentChest0','DocumentChest1','ServiceJar0','ServiceJar3','EntryAmphora0','WovenBasket0','TeachingMat'):
        low=R.bounds(ob(name))[0][2];bed=.38 if name in ('DocumentChest1','ServiceJar3') else .315
        gap=low-bed;rows.append({'interface':name+' to local floor/paving','signed_gap':gap,'allowed':[-.11,.001],'passed':-.11<=gap<=.001})
    rows.append({'interface':'all rubble starts on paving/wing floor','passed':all(abs(R.bounds(o)[0][2]-.32)<1e-5 for o in bpy.data.scenes['PS_Gundeshapur'].objects if '__Debris' in o.name and 'LOD' not in o.name)})
    result={'passed':all(r['passed'] for r in rows),'interfaces':rows,'intentional_intersections':'Structural bearing overlaps; inset plaster-loss applique 1 mm; working props settle slightly into uneven paving; masonry rubble clusters may intersect.'}
    (R.ROOT/'evidence/contact-checks.json').write_text(json.dumps(result,indent=2)+'\n');print('CONTACTS',result['passed'],len(rows));return result
