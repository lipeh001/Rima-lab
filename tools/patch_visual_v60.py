#!/usr/bin/env python3
from pathlib import Path
import html,json,re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V60_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-consistent-heart-favorites-v60' in h: raise SystemExit('V60_FAIL: patch já aplicado')
if 'rimalab-final-polish-v59' not in h or 'rimalab-favorites-layout-runtime-v43' not in h or 'rimalab-player-stage-gate-runtime-v51' not in h:
 raise SystemExit('V60_FAIL: base 3.3.7/V59/V43/V51 ausente')

# Correct the source catalog itself, not just the rendered label.
def clean_title(value):
 s=str(value or '')
 for _ in range(10):
  n=html.unescape(s)
  if n==s: break
  s=n
 return re.sub(r'[\s\u00a0]+',' ',s.replace('\u200b','').replace('\ufeff','')).strip()
def clean_catalog(obj):
 if isinstance(obj,dict):
  for k,v in list(obj.items()):
   if k.lower() in ('name','title') and isinstance(v,str): obj[k]=clean_title(v)
   else: clean_catalog(v)
 elif isinstance(obj,list):
  if len(obj)>1 and isinstance(obj[1],str) and (len(obj)>4 or isinstance(obj[0],(str,int))): obj[1]=clean_title(obj[1])
  for v in obj: clean_catalog(v)
for rel in ('app/src/main/assets/beats/catalog-seed.json','app/src/main/assets/beats/boom-bap-extra.json'):
 p=root/rel
 if p.exists():
  data=json.loads(p.read_text(encoding='utf-8'))
  clean_catalog(data)
  p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

# Keep the display-time sanitizer resilient to multiply-encoded imported titles.
if 'function rimaV59CleanTitle(value){' not in h: raise SystemExit('V60_FAIL: normalizador V59 ausente')
h=h.replace('for(let i=0;i<4;i++){','for(let i=0;i<10;i++){',1)

# Validate selected library beats against the entire catalog. Favorites can point to a category
# different from the currently active selector; the old check incorrectly trusted only ZS.s.
old="const selected=ZS.k==='syn'||(ZS.k==='lib'&&!!ZS.key&&Array.isArray(ZLIB[ZS.s])&&ZLIB[ZS.s][1].some(x=>zKey(x)===ZS.key));"
new="""let selectedTrack=null;
 if(ZS.k==='lib'&&ZS.key){
  for(const cat of Object.keys(ZLIB||{})){
   const list=ZLIB[cat]&&ZLIB[cat][1];
   if(!Array.isArray(list))continue;
   const index=list.findIndex(x=>zKey(x)===String(ZS.key));
   if(index>=0){selectedTrack={cat,index};break}
  }
 }
 if(selectedTrack){ZS.s=selectedTrack.cat;ZS.i=selectedTrack.index}
 const selected=ZS.k==='syn'||!!selectedTrack;"""
if h.count(old)!=1: raise SystemExit('V60_FAIL: validação de seleção lvStart não corresponde')

h=h.replace(old,new,1)

# Make the Favorites toolbar use a separate, regular-weight label and count.
sid='rimalab-favorites-layout-runtime-v43'
a=h.find('<script id="'+sid+'">')
if a<0: raise SystemExit('V60_FAIL: runtime V43 não encontrado')
start=h.find('>',a)+1;end=h.find('</script>',start)
js=h[start:end]
oldbar="b.innerHTML='♥ Favoritos <span class=\"rima-v29-count\">'+count()+'</span>';"
newbar="b.innerHTML='<span class=\"rima-v60-heart-glyph\" aria-hidden=\"true\">♥</span><span class=\"rima-v60-fav-label\">Favoritos</span><span class=\"rima-v29-count\">'+count()+'</span>';"
if js.count(oldbar)!=1: raise SystemExit('V60_FAIL: markup do botão Favoritos não corresponde')
js=js.replace(oldbar,newbar,1)
h=h[:start]+js+h[end:]

css=r'''<style id="rimalab-consistent-heart-favorites-v60">
/* The Favorites list is the same .mc component as the regular category list. */
#bp .rima-v43-fav-play,#bq .rima-v43-fav-play,#bbq .rima-v43-fav-play{
 display:block!important;box-sizing:border-box!important;width:100%!important;min-width:0!important;max-width:100%!important;
 min-height:0!important;height:auto!important;margin:0!important;padding:10px 12px!important;
 border:2px solid var(--ink)!important;border-radius:6px!important;
 background:var(--card)!important;color:var(--ink)!important;box-shadow:none!important;
 font-family:Anton,Impact,sans-serif!important;font-size:20px!important;font-weight:400!important;
 letter-spacing:normal!important;text-align:left!important;text-transform:none!important;
 line-height:1.15!important;white-space:normal!important;overflow-wrap:anywhere!important
}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{
 display:block!important;max-width:100%!important;margin:0!important;overflow:hidden!important;
 font-family:Anton,Impact,sans-serif!important;font-size:20px!important;font-weight:400!important;
 letter-spacing:normal!important;line-height:1.15!important
}
/* Match the exact active .mc state: yellow surface, dark text, same shadow and border. */
#bp .rima-v43-fav-play.on,#bq .rima-v43-fav-play.on,#bbq .rima-v43-fav-play.on,
#bp .rima-v43-fav-play.is-selected,#bq .rima-v43-fav-play.is-selected,#bbq .rima-v43-fav-play.is-selected{
 background:var(--ac)!important;color:var(--on)!important;border:2px solid var(--ink)!important;
 border-left:2px solid var(--ink)!important;box-shadow:3px 3px 0 var(--ink)!important
}
#bp .rima-v43-fav-play.on b,#bq .rima-v43-fav-play.on b,#bbq .rima-v43-fav-play.on b,
#bp .rima-v43-fav-play.is-selected b,#bq .rima-v43-fav-play.is-selected b,#bbq .rima-v43-fav-play.is-selected b{color:var(--on)!important}
#bp .rima-v43-fav-row.is-selected,#bq .rima-v43-fav-row.is-selected,#bbq .rima-v43-fav-row.is-selected{
 background:transparent!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.075)!important;
 border-radius:0!important;box-shadow:none!important;outline:0!important
}
/* Remove the uneven gap between favorite title, artist and offline status. */
#bp .rima-v43-fav-row>.beat-info,#bq .rima-v43-fav-row>.beat-info,#bbq .rima-v43-fav-row>.beat-info{
 gap:0!important;min-width:0!important
}
#bp .rima-v43-fav-row .beat-meta,#bq .rima-v43-fav-row .beat-meta,#bbq .rima-v43-fav-row .beat-meta{
 display:flex!important;align-items:center!important;flex-wrap:nowrap!important;gap:6px!important;
 min-width:0!important;margin:0!important;padding:3px 4px 0!important
}
#bp .rima-v43-fav-row .beat-artist,#bq .rima-v43-fav-row .beat-artist,#bbq .rima-v43-fav-row .beat-artist{
 flex:0 1 auto!important;min-width:0!important;max-width:42%!important;overflow:hidden!important;
 text-overflow:ellipsis!important;white-space:nowrap!important
}
#bp .rima-v43-fav-row .okc,#bq .rima-v43-fav-row .okc,#bbq .rima-v43-fav-row .okc{
 flex:0 0 auto!important;white-space:nowrap!important;font-size:11px!important;line-height:1.15!important
}

/* One centered, slightly fuller heart glyph in every favorite button, including the player. */
#bp .rima-v29-fav,#bq .rima-v29-fav,#bbq .rima-v29-fav,
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,
#pbar #rima-v29-player-heart{
 position:relative!important;display:grid!important;place-items:center!important;
 box-sizing:border-box!important;padding:0!important;font-size:0!important;line-height:1!important;
 text-align:center!important;transform:none!important
}
#bp .rima-v29-fav::before,#bq .rima-v29-fav::before,#bbq .rima-v29-fav::before,
#bp .rima-v43-fav-heart::before,#bq .rima-v43-fav-heart::before,#bbq .rima-v43-fav-heart::before,
#pbar #rima-v29-player-heart::before{
 content:'♡';display:block!important;position:static!important;margin:0!important;padding:0!important;
 font-family:Arial,sans-serif!important;font-size:20px!important;font-weight:900!important;
 font-stretch:normal!important;letter-spacing:-1px!important;line-height:1!important;
 transform:scaleY(.86) scaleX(1.04)!important;text-align:center!important
}
#bp .rima-v29-fav.on::before,#bq .rima-v29-fav.on::before,#bbq .rima-v29-fav.on::before,
#bp .rima-v29-fav[aria-pressed="true"]::before,#bq .rima-v29-fav[aria-pressed="true"]::before,#bbq .rima-v29-fav[aria-pressed="true"]::before,
#bp .rima-v43-fav-heart::before,#bq .rima-v43-fav-heart::before,#bbq .rima-v43-fav-heart::before,
#pbar #rima-v29-player-heart.on::before,#pbar #rima-v29-player-heart[aria-pressed="true"]::before{content:'♥'!important}
#pbar #rima-v29-player-heart{width:30px!important;min-width:30px!important;max-width:30px!important;height:30px!important;min-height:30px!important;max-height:30px!important;flex:0 0 30px!important}
#pbar #rima-v29-player-heart::before{font-size:20px!important}

/* Toolbar label and count are intentionally regular weight; category counts get breathing room. */
#bp .rima-v43-toggle,#bq .rima-v43-toggle,#bbq .rima-v43-toggle{
 display:flex!important;align-items:center!important;justify-content:center!important;gap:6px!important;
 font-weight:500!important;letter-spacing:normal!important
}
#bp .rima-v43-toggle .rima-v60-fav-label,#bq .rima-v43-toggle .rima-v60-fav-label,#bbq .rima-v43-toggle .rima-v60-fav-label{font-weight:500!important}
#bp .rima-v43-toggle .rima-v29-count,#bq .rima-v43-toggle .rima-v29-count,#bbq .rima-v43-toggle .rima-v29-count{font-weight:500!important}
.rima-v60-heart-glyph{display:inline-flex!important;align-items:center!important;justify-content:center!important;font-family:Arial,sans-serif!important;font-size:20px!important;font-weight:900!important;line-height:1!important;transform:scaleY(.86) scaleX(1.04)!important}
.rima-v50-category-row{display:flex!important;align-items:stretch!important;gap:6px!important;overflow:visible!important}
.rima-v50-category-row>.tag.chip{
 display:flex!important;align-items:center!important;justify-content:center!important;gap:4px!important;
 box-sizing:border-box!important;min-width:0!important;white-space:nowrap!important;overflow:visible!important;
 font-weight:500!important
}
.rima-v50-category-row>.tag.chip small{display:inline-block!important;flex:0 0 auto!important;margin-left:3px!important;font-size:.82em!important;font-weight:500!important;line-height:1!important}

/* Landscape: use a bounded flex column, then a horizontal strip. Avoid the indefinite-height grid
   that caused cards to overlap the category row in the previous build. */
@media(orientation:landscape) and (min-width:560px){
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage){
  display:flex!important;flex-direction:column!important;align-items:stretch!important;
  box-sizing:border-box!important;width:100%!important;height:100%!important;min-height:0!important;
  max-height:100%!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq{
  display:flex!important;position:relative!important;flex:1 1 0%!important;flex-direction:column!important;
  gap:5px!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;
  min-width:0!important;min-height:120px!important;height:auto!important;max-height:none!important;
  overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>p.mut:first-child{
  display:block!important;flex:0 0 12px!important;height:12px!important;min-height:12px!important;
  margin:0!important;padding:0!important;font-size:9px!important;line-height:12px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row{
  display:flex!important;flex:0 0 34px!important;flex-wrap:nowrap!important;align-items:stretch!important;
  width:100%!important;height:34px!important;min-height:34px!important;margin:0!important;padding:0!important;gap:5px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row>.tag.chip{
  display:flex!important;flex:1 1 0%!important;width:auto!important;max-width:none!important;min-width:0!important;
  height:34px!important;min-height:34px!important;padding:4px 2px!important;font-size:clamp(9px,1vw,12px)!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools{
  display:flex!important;flex:0 0 36px!important;position:relative!important;width:100%!important;
  height:36px!important;min-height:36px!important;margin:0!important;padding:0!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools button{
  width:100%!important;height:36px!important;min-height:36px!important;margin:0!important;padding:4px 8px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden]),
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden]){
  display:flex!important;flex:1 1 0%!important;flex-direction:row!important;flex-wrap:nowrap!important;
  align-items:stretch!important;gap:8px!important;box-sizing:border-box!important;width:100%!important;
  max-width:100%!important;min-width:0!important;min-height:68px!important;height:auto!important;
  max-height:130px!important;margin:0!important;padding:4px 5px!important;
  overflow-x:auto!important;overflow-y:hidden!important;overscroll-behavior-x:contain!important;
  -webkit-overflow-scrolling:touch!important;touch-action:pan-x pan-y!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden])>.bi,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden])>.rima-v43-fav-row{
  display:flex!important;flex:0 0 clamp(190px,25vw,280px)!important;flex-direction:row!important;
  align-items:center!important;box-sizing:border-box!important;width:clamp(190px,25vw,280px)!important;
  min-width:0!important;max-width:none!important;height:100%!important;min-height:0!important;
  margin:0!important;padding:5px!important;gap:7px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.catalog-attribution,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsw{display:none!important}
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V60_FAIL: </body> ausente')
h=h[:pos]+css+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='79': raise SystemExit('V60_FAIL: versionCode base não é 79')
g=g[:m.start(1)]+'80'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.3.7': raise SystemExit('V60_FAIL: versionName base não é 3.3.7')
g=g[:m.start(1)]+'3.3.8'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V60_OK: catalog source normalization; global favorite-key validation; matching Favorites selection/font/colors; centered consistent heart; non-bold labels/counts; stable horizontal flex selector; 3.3.8/code80')
