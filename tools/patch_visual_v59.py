#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V59_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-final-polish-v59' in h: raise SystemExit('V59_FAIL: patch já aplicado')
if 'rimalab-stage-selector-favorites-v58' not in h or 'rimalab-player-stage-gate-runtime-v51' not in h: raise SystemExit('V59_FAIL: base V58/V51 ausente')
helper=r'''function rimaV59CleanTitle(value){
 let s=String(value==null?'':value);
 for(let i=0;i<4;i++){
  const next=s.replace(/&amp;/gi,'&').replace(/&quot;/gi,'"').replace(/&#0*34;|&#x0*22;/gi,'"').replace(/&apos;|&#0*39;|&#x0*27;/gi,"'").replace(/&nbsp;|&#0*160;/gi,' ');
  if(next===s)break;s=next;
 }
 return s.normalize('NFC').replace(/[\u200B-\u200D\uFEFF]/g,'').replace(/[\s\u00A0]+/gu,' ').trim();
}
'''
needle='function zBpick(live){'
if h.count(needle)!=1: raise SystemExit('V59_FAIL: zBpick não encontrado')
h=h.replace(needle,helper+needle,1)
if 'esc(x[1])' not in h: raise SystemExit('V59_FAIL: título da lista não encontrado')
h=h.replace('esc(x[1])','esc(rimaV59CleanTitle(x[1]))',1)
old="esc(String(t.x[1]||'').normalize('NFC').replace(/\\s+/gu,' ').trim())"
if h.count(old)!=1: raise SystemExit('V59_FAIL: título dos Favoritos não encontrado')
h=h.replace(old,"esc(rimaV59CleanTitle(t.x[1]||''))",1)
extra=root/'app/src/main/assets/beats/boom-bap-extra.json'
if extra.exists():
 data=json.loads(extra.read_text(encoding='utf-8'))
 def clean_obj(o):
  if isinstance(o,dict):
   for k,v in list(o.items()):
    if k in ('name','title') and isinstance(v,str):
     o[k]=re.sub(r'\s+',' ',v.replace('&quot;','"').replace('&amp;','&').replace('&nbsp;',' ')).strip()
    else: clean_obj(v)
  elif isinstance(o,list):
   for v in o: clean_obj(v)
 clean_obj(data)
 extra.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
css=r'''<style id="rimalab-final-polish-v59">
/* Favorites: same typography and selected feedback as the regular .mc beat cards. */
#bp .rima-v43-fav-play,#bq .rima-v43-fav-play,#bbq .rima-v43-fav-play{
 box-sizing:border-box!important;min-height:50px!important;height:auto!important;padding:9px 12px!important;
 font-family:Anton,Impact,'Arial Narrow',sans-serif!important;font-size:16px!important;font-weight:400!important;
 letter-spacing:.6px!important;text-transform:uppercase!important;line-height:1.12!important;
 border:1px solid rgba(255,255,255,.10)!important;border-radius:14px!important;
 background:var(--card,rgba(255,255,255,.025))!important;color:var(--ink,#f2f5eb)!important;
 box-shadow:none!important;outline:0!important
}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{
 font-family:Anton,Impact,'Arial Narrow',sans-serif!important;font-size:16px!important;font-weight:400!important;
 letter-spacing:.6px!important;text-transform:uppercase!important;line-height:1.12!important
}
#bp .rima-v43-fav-row.is-selected,#bq .rima-v43-fav-row.is-selected,#bbq .rima-v43-fav-row.is-selected{
 border:0!important;border-bottom:1px solid rgba(255,255,255,.075)!important;
 border-radius:0!important;background:transparent!important;box-shadow:none!important;outline:0!important
}
#bp .rima-v43-fav-play.is-selected,#bq .rima-v43-fav-play.is-selected,#bbq .rima-v43-fav-play.is-selected{
 border:1px solid rgba(239,207,106,.95)!important;border-left:4px solid #e5c45b!important;
 background:linear-gradient(105deg,rgba(229,196,91,.22),rgba(229,196,91,.08))!important;
 color:#fff1b5!important;box-shadow:none!important;outline:0!important
}
#bp .rima-v43-fav-play.is-selected b,#bq .rima-v43-fav-play.is-selected b,#bbq .rima-v43-fav-play.is-selected b{color:#ffe39a!important}

/* Player heart uses the same 27px tap target as shuffle/repeat; only the glyph is optically shorter. */
#pbar #rima-v29-player-heart{
 display:grid!important;place-items:center!important;box-sizing:border-box!important;
 width:27px!important;min-width:27px!important;max-width:27px!important;
 height:27px!important;min-height:27px!important;max-height:27px!important;
 flex:0 0 27px!important;padding:0!important;font-size:0!important;line-height:1!important;
 font-family:Arial,sans-serif!important;font-stretch:normal!important;transform:none!important
}
#pbar #rima-v29-player-heart::before{
 content:'♡';display:block!important;font-family:Arial,sans-serif!important;font-size:16px!important;
 line-height:1!important;font-weight:700!important;transform:scaleY(.82)!important;
 -webkit-text-stroke:0!important;text-shadow:none!important
}
#pbar #rima-v29-player-heart[aria-pressed="true"]::before{content:'♥'!important}
@media(orientation:landscape){
 #pbar #rima-v29-player-heart{width:29px!important;min-width:29px!important;max-width:29px!important;height:29px!important;min-height:29px!important;max-height:29px!important;flex-basis:29px!important}
 #pbar #rima-v29-player-heart::before{font-size:17px!important}
}

/* When setup preview reveals the fixed player, leave scroll space after Ouvir and Começar treino. */
body.rima-v51-player-eligible #train-step-2{padding-bottom:calc(112px + env(safe-area-inset-bottom,0px))!important}
body.rima-v51-player-eligible #train-step-2 .training-footer{margin-bottom:calc(12px + env(safe-area-inset-bottom,0px))!important}

/* Landscape: proven two-column header, with a real horizontal strip of visible beat cards. */
@media(orientation:landscape) and (min-width:560px){
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq{
  display:grid!important;position:relative!important;flex:1 1 0%!important;
  grid-template-columns:minmax(0,1fr) 88px!important;grid-template-rows:30px 12px minmax(0,1fr)!important;
  column-gap:7px!important;row-gap:3px!important;box-sizing:border-box!important;
  width:100%!important;max-width:100%!important;min-width:0!important;height:100%!important;
  max-height:100%!important;min-height:0!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>p.mut:first-child{display:none!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row{
  grid-column:1!important;grid-row:1!important;display:flex!important;flex-wrap:nowrap!important;
  width:100%!important;min-width:0!important;height:30px!important;min-height:30px!important;
  margin:0!important;padding:0!important;gap:4px!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row>.tag.chip{
  display:flex!important;flex:1 1 0!important;width:auto!important;min-width:0!important;max-width:none!important;
  height:30px!important;min-height:30px!important;align-items:center!important;justify-content:center!important;
  margin:0!important;padding:4px 2px!important;font-size:clamp(8px,.95vw,11px)!important;
  line-height:1.05!important;white-space:nowrap!important;overflow:hidden!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools{
  grid-column:2!important;grid-row:1!important;display:flex!important;width:100%!important;min-width:0!important;
  height:30px!important;min-height:30px!important;margin:0!important;padding:0!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools button{
  width:100%!important;height:30px!important;min-height:30px!important;padding:2px!important;font-size:10px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>p.mut:not(:first-child){
  grid-column:1 / -1!important;grid-row:2!important;display:block!important;
  height:12px!important;min-height:12px!important;max-height:12px!important;margin:0!important;padding:0!important;
  overflow:hidden!important;white-space:nowrap!important;text-overflow:ellipsis!important;font-size:8px!important;line-height:12px!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden]),
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden]){
  grid-column:1 / -1!important;grid-row:3!important;display:flex!important;flex-direction:row!important;
  flex-wrap:nowrap!important;align-items:stretch!important;gap:8px!important;
  box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;
  min-height:64px!important;height:100%!important;max-height:none!important;margin:0!important;padding:4px 5px!important;
  overflow-x:auto!important;overflow-y:hidden!important;overscroll-behavior-x:contain!important;
  overscroll-behavior-y:none!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-x pan-y!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden])>.bi,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden])>.rima-v43-fav-row{
  display:flex!important;flex:0 0 clamp(190px,27vw,310px)!important;
  box-sizing:border-box!important;width:clamp(190px,27vw,310px)!important;min-width:0!important;max-width:none!important;
  height:100%!important;min-height:0!important;align-items:center!important;gap:7px!important;
  margin:0!important;padding:5px!important;scroll-snap-align:start!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl>.bi>.beat-info,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist>.rima-v43-fav-row>.beat-info{
  flex:1 1 0%!important;min-width:0!important;max-width:100%!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl>.bi .mc,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist .rima-v43-fav-play{
  min-height:52px!important;height:auto!important;padding:8px 9px!important;font-size:clamp(12px,1.2vw,15px)!important
 }
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.catalog-attribution,
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsw{display:none!important}
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V59_FAIL: </body> ausente')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='78': raise SystemExit('V59_FAIL: versionCode base não é 78')
g=g[:m.start(1)]+'79'+g[m.end(1):]
m=re.search(r"\bversionName\s*(?:=\s*)?['\"]([^'\"]+)['\"]",g)
if not m or m.group(1)!='3.3.6': raise SystemExit('V59_FAIL: versionName base não é 3.3.6')
g=g[:m.start(1)]+'3.3.7'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V59_OK: title normalization, Favorites typography/selection, compact player heart, setup scroll reserve, horizontal beat strip; 3.3.7/code79')
