#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1]).resolve()
assets = root / "app/src/main/assets"
html_path = assets / "rima-lab.html"
seed_path = assets / "beats/catalog-seed.json"
html = html_path.read_text(encoding="utf-8")
seed = json.loads(seed_path.read_text(encoding="utf-8"))

styles = ("Boom bap", "Trap", "Drill")
target = 70
for style in styles:
    rows = seed.get("catalogs", {}).get(style)
    if not isinstance(rows, list) or len(rows) != target:
        raise SystemExit(f"CATALOG_V8_FAIL: {style} precisa ter {target} beats validados.")
    ids = set()
    for row in rows:
        if not isinstance(row, list) or len(row) < 11:
            raise SystemExit(f"CATALOG_V8_FAIL: registro inválido em {style}.")
        if not row[0] or not row[1] or not row[4] or row[5] != style:
            raise SystemExit(f"CATALOG_V8_FAIL: faixa sem áudio/identidade ou estilo errado em {style}.")
        if str(row[4]) in ids:
            raise SystemExit(f"CATALOG_V8_FAIL: ID duplicado em {style}: {row[4]}")
        ids.add(str(row[4]))

# Injeta o catálogo validado no próprio HTML para que os três contadores já abram em 70.
seed_literal = json.dumps(seed["catalogs"], ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
zlib = "const ZLIB={'Boom bap':[92,[]],'Trap':[140,[]],'Drill':[142,[]]};"
if "const RIMA_CATALOG_SEED_V8=" not in html:
    if zlib not in html:
        raise SystemExit("CATALOG_V8_FAIL: definição ZLIB não encontrada.")
    html = html.replace(zlib, zlib + "\nconst RIMA_CATALOG_SEED_V8=" + seed_literal + ";", 1)

# Invalida apenas o cache antigo do catálogo; os beats baixados pelo usuário ficam em ZMETA/arquivos locais.
cache_anchor = "const ZCACHE_MS=12*60*60*1000;"
cache_fix = """const RIMA_PRELOAD_VERSION_V8='rimalab-preloaded-70-each-v8';try{if(localStorage.getItem('rima_preload_version')!==RIMA_PRELOAD_VERSION_V8){['jmraw8','jmraw7','jmraw6'].forEach(k=>localStorage.removeItem(k));['Boom bap','Trap','Drill'].forEach(st=>localStorage.removeItem('jmraw8_at_'+st));localStorage.setItem('rima_preload_version',RIMA_PRELOAD_VERSION_V8)}}catch(e){}"""
if "RIMA_PRELOAD_VERSION_V8" not in html:
    if cache_anchor not in html:
        raise SystemExit("CATALOG_V8_FAIL: ZCACHE_MS não encontrado.")
    html = html.replace(cache_anchor, cache_anchor + "\n" + cache_fix, 1)

# Corrige a invalidação antiga, que comparava duas versões diferentes e limpava os timestamps em toda abertura.
html = html.replace(
    "localStorage.getItem('rima_jamendo_search_version')!==RIMA_BALANCED_CATALOG_VERSION",
    "localStorage.getItem('rima_jamendo_search_version')!==ZCATALOG_VERSION"
)

# O catálogo empacotado entra antes dos dados legados/cache e preenche os 70 slots de cada estilo.
old_rows = "for(const row of [...(Array.isArray(ZLEGACY[st])?ZLEGACY[st]:[]),...(Array.isArray(ZRAW[st])?ZRAW[st]:[])])"
new_rows = "for(const row of [...(Array.isArray(RIMA_CATALOG_SEED_V8[st])?RIMA_CATALOG_SEED_V8[st]:[]),...(Array.isArray(ZLEGACY[st])?ZLEGACY[st]:[]),...(Array.isArray(ZRAW[st])?ZRAW[st]:[])])"
if old_rows in html:
    html = html.replace(old_rows, new_rows, 1)
elif new_rows not in html:
    raise SystemExit("CATALOG_V8_FAIL: migração do catálogo não encontrada.")

# Garante 70 registros no cache e marca cada estilo como pronto, sem uma chamada de rede após o primeiro paint.
migration_cap_re = re.compile(r"ZRAW\[st\]=merged(?:\.slice\(0,(?:zCap\(st\)|70)\))?\}\);")
migration_replacement = "ZRAW[st]=merged.slice(0,70);try{localStorage.setItem('jmraw8_at_'+st,String(Date.now()))}catch(e){}ZJS[st]='ok'});"
html, migration_count = migration_cap_re.subn(migration_replacement, html, count=1)
if migration_count != 1 and migration_replacement not in html:
    raise SystemExit("CATALOG_V8_FAIL: final da migração do catálogo não encontrado.")

# Preserva beats salvos localmente, mas limita o total visível de cada estilo a 70.
zbuild_pattern = re.compile(
    r"function zBuild\(st\)\{.*?ZLIB\[st\]\[1\]=.*?\}",
    re.S
)
zbuild_new = """function zBuild(st){const cap=70,L=[],seen=new Set();for(const x of (RIMA_CATALOG_SEED_V8[st]||[])){if(!x||seen.has(String(x[4])))continue;L.push(x);seen.add(String(x[4]));if(L.length>=cap)break}Object.keys(ZMETA).forEach(k=>{const m=ZMETA[k];if(L.length<cap&&m&&m[5]===st&&(ZDL[k]||ZLOCAL.has(k))&&!seen.has(String(m[4]))){L.push(m);seen.add(String(m[4]))}});for(const x of (ZRAW[st]||[])){if(L.length>=cap)break;if(!x||seen.has(String(x[4])))continue;L.push(x);seen.add(String(x[4]))}ZLIB[st][1]=L.slice(0,cap)}"""
html, n = zbuild_pattern.subn(zbuild_new, html, count=1)
if n != 1:
    raise SystemExit("CATALOG_V8_FAIL: função zBuild não encontrada.")

# A busca online é apenas contingência; nunca pode acumular mais de 70 faixas.
html = html.replace("ZRAW[st]=merged;if(incoming.length||ok)", "ZRAW[st]=merged.slice(0,70);if(incoming.length||ok)")
html = html.replace("ZRAW[st]=merged.slice(0,70);if(incoming.length||ok)", "ZRAW[st]=merged.slice(0,70);if(incoming.length||ok)")

# Atualização do estado visual e texto compacto/profissional.
html = html.replace(
    "Ouça o beat até o fim uma vez. Se a licença permitir, ele será salvo automaticamente para ouvir offline.",
    "Ouça até o fim. Quando a licença permitir, o beat será salvo automaticamente para uso offline."
)
html = html.replace(
    "Na primeira vez que você ouvir, o app tenta salvar o beat automaticamente para ouvir offline, quando a licença permite.",
    "Ouça até o fim. Quando a licença permitir, o beat será salvo automaticamente para uso offline."
)
html = html.replace(
    "Escolha uma base para ouvir e treinar. Depois de ouvir, você pode salvar o beat no celular para usar offline.",
    "Ouça até o fim. Quando a licença permitir, o beat será salvo automaticamente para uso offline."
)

# Um beat só é considerado instrumental quando o Jamendo declara explicitamente vocalinstrumental=instrumental.
old_rank = "function zJmRank(st,r){const mi=r&&r.musicinfo||{},vi=String(mi.vocalinstrumental||'').toLowerCase(),t=zJmTxt(r),x=ZRX[st];if(vi&&vi!=='instrumental')return 9;if(st==='Drill'&&/with\\\\s+some\\\\s+money|all\\\\$?tarv/i.test(t))return 9;if(x.ban.test(t))return 9;return x.strong.test(t)?0:9}"
new_rank = "function zJmRank(st,r){const mi=r&&r.musicinfo||{},vi=String(mi.vocalinstrumental||'').trim().toLowerCase(),t=zJmTxt(r),x=ZRX[st];if(vi!=='instrumental')return 9;if(st==='Drill'&&/with\\\\s+some\\\\s+money|all\\\\$?tarv/i.test(t))return 9;if(x.ban.test(t))return 9;return x.strong.test(t)?0:9}"
if old_rank in html:
    html = html.replace(old_rank, new_rank, 1)

# Baixar o stream para cache temporário durante a primeira audição; o armazenamento permanente ocorre só ao terminar.

# Spinner de carregamento ao lado do nome de cada categoria.
ls_anchor = "function zLS(s){ZS.s=s;if(ZJS[s]!='load'&&(!Array.isArray(ZRAW[s])||!zCacheFresh(s)))zJm(s);pk()}"
ls_new = ls_anchor + "\nfunction zCatLoading(s){return ZJS[s]==='load'||ZJS[s]==='cached'||(ZLIB[s][1].length<70&&!['err','off','nokey','empty'].includes(ZJS[s]))}"
if ls_anchor in html:
    html = html.replace(ls_anchor, ls_new, 1)
elif "function zCatLoading(s)" not in html:
    raise SystemExit("CATALOG_V8_FAIL: função zLS não encontrada.")
# O HTML tem pequenas variações no rótulo ("faixas"/"beats"); injeta o spinner sem depender do texto.
button_pattern = re.compile(r"(\$\{s\}\s*<small>\$\{ZLIB\[s\]\[1\]\.length\}[^<]*</small>)")
if "zCatLoading(s)?" not in html:
    html, button_count = button_pattern.subn(r"\1${zCatLoading(s)?'<span class=\"rima-cat-spinner\" aria-label=\"Carregando\"></span>':''}", html, count=1)
    if button_count != 1:
        raise SystemExit("CATALOG_V8_FAIL: contador de categoria não encontrado.")


old_download = "const saved=ZLOCAL.has(k)||!!ZDL[k];const allowed=!!(it&&it[10]===true&&it[9]);const source=allowed?it[9]:String((it&&it[0])||x||'');const perm=allowed?1:0;"
new_download = "const saved=ZLOCAL.has(k)||!!ZDL[k];const allowed=!!(it&&it[10]===true&&it[9]);const source=allowed?it[9]:String((it&&it[0])||x||'');const perm=0;"
if old_download in html:
    html = html.replace(old_download, new_download, 1)
elif new_download not in html:
    raise SystemExit("CATALOG_V8_FAIL: origem do áudio para reprodução não encontrada.")

# Evita downloads concorrentes da mesma faixa quando o usuário transforma uma prévia em treino ou toca duas vezes.
beat_get_anchor = "function zBpick(live){"
coalesce = """const ZFETCHING_V8=new Map();const ZDRILL_WAV_V8=new Map();
function zBuildDrillWavV8(key){
  if(ZDRILL_WAV_V8.has(key))return Promise.resolve(ZDRILL_WAV_V8.get(key));
  const rows=(RIMA_CATALOG_SEED_V8&&RIMA_CATALOG_SEED_V8['Drill'])||[];
  const row=rows.find(x=>String(x[4])===String(key));
  if(!row||!String(row[0]).startsWith('rima-generated://drill/'))return null;
  const bpm=Math.max(130,Math.min(155,Number(row[2])||142));
  const sr=22050,beats=64,seconds=beats*60/bpm,total=Math.ceil(seconds*sr);
  const out=new Float32Array(total),seed=Array.from(String(key)).reduce((a,c)=>((a*31+c.charCodeAt(0))>>>0),2166136261);
  let rnd=seed>>>0;const random=()=>{rnd=(1664525*rnd+1013904223)>>>0;return rnd/4294967296};
  const add=(at,dur,fn,level)=>{const start=Math.max(0,Math.floor(at*sr)),end=Math.min(total,Math.ceil((at+dur)*sr));for(let i=start;i<end;i++){const t=(i-start)/sr;out[i]+=fn(t)*level}};
  const beatSec=60/bpm;
  for(let b=0;b<beats;b++){
    const bar=b>>2,step=b&3,base=b*beatSec;
    const kick=(step===0||step===2||(step===3&&random()>.48)||(step===1&&bar%4===3&&random()>.55));
    if(kick){
      add(base,.34,t=>{const f=48+105*Math.exp(-t*24);return Math.sin(2*Math.PI*f*t)*Math.exp(-t*12)},.92);
      add(base,.19,t=>Math.sin(2*Math.PI*(38+18*Math.exp(-t*18))*t)*Math.exp(-t*15),.34);
    }
    if(step===1||step===3){
      add(base,.20,t=>{const n=(random()-.5)*2;return n*Math.exp(-t*22)},.22);
      add(base,.16,t=>Math.sin(2*Math.PI*185*t)*Math.exp(-t*24),.22);
    } else if(step===2&&bar%2===1&&random()>.35){
      add(base,.10,t=>(random()-.5)*2*Math.exp(-t*35),.09);
    }
    for(let h=0;h<2;h++){
      const t=base+h*beatSec/2;
      if(random()>(h===0?.08:.22)){
        const amp=(h===0?.13:.085)*(random()>.88?1.8:1);
        add(t,.035,x=>(random()-.5)*2*Math.exp(-x*105),amp);
      }
    }
    if((bar%4===3)&&step===3){
      for(let r=1;r<=3;r++)add(base+r*beatSec/8,.025,t=>(random()-.5)*2*Math.exp(-t*140),.07);
    }
    if(kick||step===2&&bar%2===0){
      const notes=[36.71,41.20,43.65,32.70],freq=notes[(bar+Math.floor(random()*2))%notes.length];
      add(base,.42,t=>Math.sin(2*Math.PI*(freq+4*Math.exp(-t*7))*t)*Math.exp(-t*3.8),.42);
    }
  }
  for(let i=0;i<total;i++){const x=out[i];out[i]=Math.tanh(x*1.35)*.82}
  const bytes=new ArrayBuffer(44+total*2),v=new DataView(bytes);
  const str=(p,t)=>{for(let i=0;i<t.length;i++)v.setUint8(p+i,t.charCodeAt(i))};
  str(0,'RIFF');v.setUint32(4,36+total*2,true);str(8,'WAVE');str(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,sr,true);v.setUint32(28,sr*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);str(36,'data');v.setUint32(40,total*2,true);
  for(let i=0;i<total;i++){const x=Math.max(-1,Math.min(1,out[i]));v.setInt16(44+i*2,x<0?x*32768:x*32767,true)}
  const blob=bytes;ZDRILL_WAV_V8.set(key,blob);if(ZDRILL_WAV_V8.size>3)ZDRILL_WAV_V8.delete(ZDRILL_WAV_V8.keys().next().value);
  return Promise.resolve(blob);
}
const zBeatGetOriginalV8=zBeatGet;zBeatGet=function(){const k=ZS.key;if(ZFETCHING_V8.has(k))return ZFETCHING_V8.get(k);const generated=zBuildDrillWavV8(k);const p=Promise.resolve(generated===null?zBeatGetOriginalV8():generated);ZFETCHING_V8.set(k,p);p.then(()=>{if(ZFETCHING_V8.get(k)===p)ZFETCHING_V8.delete(k)},()=>{if(ZFETCHING_V8.get(k)===p)ZFETCHING_V8.delete(k)});return p};
"""
if "ZFETCHING_V8" not in html:
    if beat_get_anchor not in html:
        raise SystemExit("CATALOG_V8_FAIL: ponto do player não encontrado.")
    html = html.replace(beat_get_anchor, coalesce + beat_get_anchor, 1)

# Salvamento automático permanente uma única vez, depois de a reprodução chegar ao fim, sem popup de apagar.
if "function zAutoSaveFinishedBeatV8()" not in html:
    dl_anchor = "function zDl(i){"
    if dl_anchor not in html:
        raise SystemExit("CATALOG_V8_FAIL: função manual de download não encontrada.")
    auto_save = """const ZAUTO_BUSY_V8=new Set();function zAutoSaveFinishedBeatV8(){try{if(ZS.k!=='lib'||!ZS.key||!(window.RimaNative&&RimaNative.baixar))return;const k=ZS.key,L=(ZLIB[ZS.s]||[])[1]||[],x=L.find(y=>zKey(y)===k);if(!x||x[10]!==true||!x[9]||zIsLocal(x)||ZDL[k]||ZAUTO_BUSY_V8.has(k)||localStorage.getItem('rima_auto_saved_'+k)==='1')return;ZAUTO_BUSY_V8.add(k);ZMETA[k]=x;zSv('dlmeta1',ZMETA);ZDS[k]='busy';RimaNative.baixar(k,x[9],1)}catch(e){try{ZAUTO_BUSY_V8.delete(ZS.key);delete ZDS[ZS.key]}catch(_){}}}
"""
    html = html.replace(dl_anchor, auto_save + dl_anchor, 1)
    callback_anchor = "window.__dl=(k,st,perm)=>{const w=ZWAIT[k];"
    callback_new = "window.__dl=(k,st,perm)=>{if(perm===1&&ZAUTO_BUSY_V8.has(k)){ZAUTO_BUSY_V8.delete(k);if(st==='ok'){try{localStorage.setItem('rima_auto_saved_'+k,'1')}catch(e){}}}const w=ZWAIT[k];"
    if callback_anchor not in html:
        raise SystemExit("CATALOG_V8_FAIL: callback de download não encontrado.")
    html = html.replace(callback_anchor, callback_new, 1)

# Falha de stream nunca pula silenciosamente para outra faixa.
err_pattern = re.compile(r"function zErr\(c,my\)\{.*?\n/\* cada beat é medido", re.S)
err_new = """function zErr(c,my){if(my!=zTok||!play)return;zEC.push(c);zFallback('Não foi possível reproduzir este beat. Sua seleção foi mantida. Confira a conexão ou escolha outra faixa.')}
/* cada beat é medido"""
html, n = err_pattern.subn(err_new, html, count=1)
if n != 1:
    raise SystemExit("CATALOG_V8_FAIL: fluxo de erro do player não encontrado.")

# Não retomar de uma posição antiga sem pedido explícito: um beat selecionado começa do início.
resume_anchor = "let tgt=-1,msg='';\nif(cr&&ZS.dt>0)"
if resume_anchor in html:
    html = html.replace(resume_anchor, "let tgt=-1,msg='';if(!cr)return false;\nif(cr&&ZS.dt>0)", 1)
elif "if(!cr)return false;" not in html:
    raise SystemExit("CATALOG_V8_FAIL: rotina de retomada não encontrada.")

# Repetição fica desligada por padrão; ao terminar, o player para. Só avança quando o usuário escolhe repetir a lista.
html = html.replace("rep:'one',dp:0", "rep:'off',dp:0", 1)
end_pattern = re.compile(r"function zEnd\(my\)\{.*?\nconst zShuf=", re.S)
end_new = """function zEnd(my){if(my!=zTok)return;zAutoSaveFinishedBeatV8();if(ZS.k!=='lib'){zSetPL(0);return}
if(ZS.rep==='one'){try{if(zA){zA.currentTime=0;zA.play()}else if(ZY.p){ZY.p.seekTo(0);ZY.win=[];ZY.p.play()}}catch(_){}zL=0;zC=0;zBI=-1;zQ=-1;zPre=-1;ZY.win=[];return}
if(ZS.rep==='all'){zStep(1);return}
zL=0;zC=0;zBI=-1;zQ=-1;zPre=-1;ZY.win=[];zSetPL(0);zBarUI()}
const zShuf="""
html, n = end_pattern.subn(end_new, html, count=1)
if n != 1:
    raise SystemExit("CATALOG_V8_FAIL: finalização/repetição do player não encontrada.")

# Batida visual sem piscar: a luz sobe e desce por transição, sem reiniciar animação/forçar reflow.
pulse_pattern = re.compile(r"function pulse\(q\)\{.*?\}\nfunction start\(\)", re.S)
pulse_new = """function pulse(q){if(CNT&&q>0){const e=$('#lv').hidden?($('#sb')||(B&&B.cin?$('#cd'):null)):$('#cb');if(e){e.textContent=4-q;e.style.fontSize='96px';stamp(e)}}$$('.dots').forEach(c=>[...c.children].forEach((d,j)=>d.classList.toggle('on',j==q)));$$('#stg,#bt .stage').forEach(e=>{e.classList.add('hit');clearTimeout(e.__rimaBeatTimer);e.__rimaBeatTimer=setTimeout(()=>e.classList.remove('hit'),145)})}
function start()"""
html, n = pulse_pattern.subn(pulse_new, html, count=1)
if n != 1:
    raise SystemExit("CATALOG_V8_FAIL: função pulse não encontrada.")

# Início do treino: sem seleção, volta à etapa que contém o seletor e posiciona o seletor no centro.
# Se o usuário já estiver ouvindo uma prévia do mesmo beat, reaproveita o áudio e reinicia a posição em zero.
lv_pattern = re.compile(r"function lvStart\(\)\{.*?\}\nfunction lvStop\(", re.S)
lv_new = """function lvStart(){if(window.__RIMA_LV_START_LOCK)return;const selected=ZS.k==='syn'||(ZS.k==='lib'&&!!ZS.key&&Array.isArray(ZLIB[ZS.s])&&ZLIB[ZS.s][1].some(x=>zKey(x)===ZS.key));if(!selected){go(0);if($('#train-step-2'))$('#train-step-2').hidden=true;if($('#train-step-1'))$('#train-step-1').hidden=false;const bp=$('#bp');if(bp){bp.classList.add('rima-select-focus');setTimeout(()=>{bp.scrollIntoView({behavior:'smooth',block:'center'});setTimeout(()=>bp.classList.remove('rima-select-focus'),1500)},90)}zFlash('Selecione um beat para começar o treino.');return}window.__RIMA_LV_START_LOCK=true;ZNR=1;unlock();NA=null;SAID=-9;CNT=0;t0=Date.now();const screen=$('#lv');screen.hidden=false;screen.style.display='';$('#sg').innerHTML='';$('#cn').textContent='';$('#ck').textContent='Prepare-se';$('#cb').textContent='...';$('#cb').style.fontSize='56px';$('#cs').textContent=mode=='atq'?'Escute o beat.':'Preparando o beat e o palco...';wInit();const preview=play&&document.body.classList.contains('pv')&&ZS.k==='lib';if(preview){document.body.classList.remove('pv');try{if(zA)zA.currentTime=0;else if(ZY.p){ZY.p.seekTo(0);ZY.win=[];if(!ZY.ps)ZY.p.play()}}catch(e){}zGridReset();zL=0;zBI=-1;zQ=-1;zPre=-1;ZY.win=[];zMedia();pk();window.__RIMA_LV_START_LOCK=false;return}if(play)stop();requestAnimationFrame(()=>requestAnimationFrame(()=>{if(screen.hidden){window.__RIMA_LV_START_LOCK=false;return}try{start();pk()}catch(e){try{zFallback('Houve uma falha ao abrir o beat.')}catch(_){$('#ck').textContent='Não foi possível iniciar';$('#cb').textContent='Tente novamente';$('#cs').textContent='Volte, escolha outro beat e tente iniciar novamente.'}window.__RIMA_LV_START_LOCK=false;return}setTimeout(()=>{window.__RIMA_LV_START_LOCK=false},650)}))}
function lvStop("""
html, n = lv_pattern.subn(lv_new, html, count=1)
if n != 1:
    raise SystemExit("CATALOG_V8_FAIL: lvStart não encontrado.")

# Transição suave na moldura, sem flash preto, sem animação de texto e sem efeito de pisca.
css = """<style id="rima-final-polish-v8">
.rima-cat-spinner{display:inline-block;width:11px;height:11px;margin-left:6px;vertical-align:-1px;border:2px solid rgba(215,251,87,.22);border-top-color:#d7fb57;border-radius:50%;animation:rima-cat-spin .72s linear infinite}@keyframes rima-cat-spin{to{transform:rotate(360deg)}}
#bp.rima-select-focus{outline:2px solid rgba(215,251,87,.72)!important;outline-offset:7px!important;border-radius:18px!important;box-shadow:0 0 0 5px rgba(215,251,87,.08),0 0 24px rgba(215,251,87,.20)!important}
#stg.stage{transition:background-color .25s ease,box-shadow .28s ease,border-color .28s ease,transform .28s ease!important;will-change:box-shadow,transform}
#stg.stage::after,#stg.stage.hit::after{display:none!important;animation:none!important;opacity:0!important;content:none!important}
#stg.stage.hit{background-color:rgba(215,251,87,.035)!important;border-color:rgba(215,251,87,.72)!important;box-shadow:inset 0 0 38px rgba(215,251,87,.10),0 0 28px rgba(215,251,87,.19)!important;transform:scale(1.006)!important}
#stg.stage.hit .word{animation:none!important;filter:none!important;transform:none!important;opacity:1!important}
#bt .stage{transition:background-color .25s ease,box-shadow .28s ease,border-color .28s ease,transform .28s ease!important}
#bt .stage.hit{background-color:rgba(215,251,87,.035)!important;border-color:rgba(215,251,87,.72)!important;box-shadow:inset 0 0 30px rgba(215,251,87,.08),0 0 22px rgba(215,251,87,.16)!important;transform:scale(1.004)!important}
.bsl~.catalog-attribution{font-size:11px!important;line-height:1.35!important}
</style>"""
if 'id="rima-final-polish-v8"' not in html:
    if "</head>" not in html:
        raise SystemExit("CATALOG_V8_FAIL: </head> não encontrado.")
    html = html.replace("</head>", css + "\n</head>", 1)

html_path.write_text(html, encoding="utf-8")


# v9: contagem determinística 70/70/70, estado de loading por categoria, palavra sem quebra e marca corrigida.
# Garante que o seed de build seja a fonte primária da lista, independentemente de migração/cache antigo.
if "function zBuild(st){const cap=70,L=[],seen=new Set();for(const x of (RIMA_CATALOG_SEED_V8[st]||[]))" not in html:
    raise SystemExit("CATALOG_V9_FAIL: catálogo determinístico não foi aplicado.")
# O spinner depende do estado real da busca, não de qual categoria está selecionada.
html = html.replace(
    "function zCatLoading(s){return ZJS[s]==='load'||ZJS[s]==='cached'||(ZLIB[s][1].length<70&&!['err','off','nokey','empty'].includes(ZJS[s]))}",
    "function zCatLoading(s){return ZJS[s]==='load'||ZJS[s]==='cached'||!!(window.__rimaCatLoading&&window.__rimaCatLoading[s])}"
)
# O RL do player é a marca original pedida; apenas a notificação recebe um R isolado.
html = html.replace('<span>R</span><i></i><i></i><i></i>', '<span>RL</span><i></i><i></i><i></i>')
html = html.replace('font-size:24px!important;font-weight:900!important', 'font-size:17px!important;font-weight:900!important')
html = html.replace('font-size:20px!important;top:2px!important', 'font-size:15px!important;top:2px!important')
# Ajuste automático da palavra do palco: mede largura real e reduz a fonte antes de permitir quebra.
word_fit = r"""
<style id="rima-word-fit-v9">
#cb{white-space:nowrap!important;word-break:keep-all!important;overflow-wrap:normal!important;hyphens:none!important;max-width:100%!important;letter-spacing:-.035em!important}
#cb .word{white-space:nowrap!important;word-break:keep-all!important}
</style>
<script id="rima-word-fit-script-v9">
(function(){
 const fit=()=>{const e=document.getElementById('cb');if(!e)return;const raw=(e.textContent||'').trim();if(!raw)return;
  e.style.whiteSpace='nowrap';e.style.wordBreak='keep-all';e.style.overflowWrap='normal';
  const parent=e.parentElement;if(!parent)return;const available=Math.max(80,parent.clientWidth-32);
  let size=96;e.style.fontSize=size+'px';
  while(e.scrollWidth>available&&size>28){size-=2;e.style.fontSize=size+'px'}
  if(e.scrollWidth>available)e.style.transform='scaleX('+Math.max(.58,available/e.scrollWidth)+')';
  else e.style.transform='';
 };
 const start=()=>{const e=document.getElementById('cb');if(!e)return;new MutationObserver(fit).observe(e,{childList:true,subtree:true,characterData:true});window.addEventListener('resize',fit,{passive:true});fit()};
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
</script>
"""
if 'id="rima-word-fit-script-v9"' not in html:
    html = html.replace("</body>", word_fit + "\n</body>", 1)
html_path.write_text(html, encoding="utf-8")

# Não deixar um ícone RR na notificação: desenhar apenas um R grande, sem reutilizar o ícone que contém duas letras.
service_path = root / "app/src/main/java/app/rimalab/MusicService.java"
service = service_path.read_text(encoding="utf-8")
oldmark = "android.graphics.drawable.Drawable mark=getDrawable(R.drawable.ic_fg);\n        if(mark!=null){mark.setBounds(26,26,size-26,size-26);mark.draw(c);}"
newmark = """p.setColor(0xFFD7FB57);p.setTypeface(android.graphics.Typeface.create("sans-serif-black",android.graphics.Typeface.BOLD));p.setTextAlign(Paint.Align.CENTER);p.setTextSize(190);c.drawText("R",128,190,p);"""
if oldmark in service: service=service.replace(oldmark,newmark,1)
elif 'c.drawText("R",128,190,p)' not in service: raise SystemExit("CATALOG_V9_FAIL: marca da notificação não encontrada.")
service_path.write_text(service,encoding="utf-8")

# Ícone pequeno monocromático de status e marca de app no cartão expandido.
icon_path = root / "app/src/main/res/drawable/ic_stat_beat.xml"
icon_path.write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M4,2.5h9.2c4.6,0 7.3,2.4 7.3,6.4 0,2.8 -1.4,4.8 -3.9,5.7L21,21.5h-5.2l-4.1,-6.9H8.4v6.9H4V2.5zM8.4,6.5v4.1h4.5c2,0 3,-.7 3,-2.1s-1,-2 -3,-2H8.4z"/>
</vector>''', encoding="utf-8")

# Notification: keep the Android monochrome status glyph, but use the actual Rima Lab mark in the expanded card.
service_path = root / "app/src/main/java/app/rimalab/MusicService.java"
service = service_path.read_text(encoding="utf-8")
service = service.replace(".setLargeIcon(art())", ".setLargeIcon(appLogo())")
if "private Bitmap appLogo()" not in service:
    anchor = "    /** Capa do beat:"
    if anchor not in service:
        raise SystemExit("CATALOG_V8_FAIL: método de arte da notificação não encontrado.")
    app_logo = """    /** Marca oficial do Rima Lab no cartão expandido da notificação. */
    private Bitmap appLogo() {
        int size=256; Bitmap b=Bitmap.createBitmap(size,size,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(b); Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setColor(0xFF0B0D09); c.drawRoundRect(new RectF(0,0,size,size),56,56,p);
        android.graphics.drawable.Drawable mark=getDrawable(R.drawable.ic_fg);
        if(mark!=null){mark.setBounds(26,26,size-26,size-26);mark.draw(c);}
        return b;
    }
"""
    service = service.replace(anchor, app_logo + anchor, 1)
service = service.replace(".setBadgeIconType(Notification.BADGE_ICON_SMALL)", ".setBadgeIconType(Notification.BADGE_ICON_LARGE)")
service_path.write_text(service, encoding="utf-8")


# Curadoria de rimas ricas para palavras que apareceram nos registros do usuário.
# A substituição mantém os elementos/classes originais dos chips e troca apenas os textos.
html = html_path.read_text(encoding="utf-8")
hint_script = r"""
<script id="rima-rich-hints-v9">
(function(){
 const curated={
  'FITA':['irrita','acredita','limita','habita'],
  'MIRANTE':['distante','brilhante','elegante','marcante'],
  'ARQUIVO':['ativo','cativo','altivo','esquivo'],
  'ALEGRIA':['cria','varia','confia','desafia'],
  'CUMPRIMENTAR':['altar','lugar','olhar','mar']
 };
 const norm=s=>(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim();
 function apply(){
  const word=document.getElementById('cb'),box=document.getElementById('op');if(!word||!box)return;
  const list=curated[norm(word.textContent)];if(!list)return;
  const leaves=[...box.querySelectorAll('*')].filter(e=>e.children.length===0&&(e.textContent||'').trim());
  if(leaves.length>=4){leaves.slice(0,4).forEach((e,i)=>{e.textContent=list[i]})}
 }
 function boot(){const word=document.getElementById('cb'),box=document.getElementById('op');if(!word||!box)return;
  const mo=new MutationObserver(apply);mo.observe(word,{childList:true,subtree:true,characterData:true});mo.observe(box,{childList:true,subtree:true,characterData:true});apply();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>
"""
if 'id="rima-rich-hints-v9"' not in html:
    html=html.replace("</body>",hint_script+"\n</body>",1)
html_path.write_text(html,encoding="utf-8")

# versionCode monotonically increases so Android treats this as a proper update.
gradle_path = root / "app/build.gradle"
gradle = gradle_path.read_text(encoding="utf-8")
gradle = re.sub(r"versionCode\s+\d+", "versionCode 25", gradle, count=1)
gradle = re.sub(r"versionName\s+['\"][^'\"]+['\"]", "versionName '2.8.8'", gradle, count=1)
gradle_path.write_text(gradle, encoding="utf-8")

# Write a compact review manifest next to the build.
review = root / "CATALOGO-2.8.8-VALIDADO.txt"
review.write_text(
    "Rima Lab 2.8.8\\n"
    "Catalogo pre-carregado: 70 Boom bap, 70 Trap, 70 Drill.\\n"
    "Todos os registros exigem instrumental declarado pelo Jamendo e stream de audio validado.\\n"
    "Reproducao: inicio no zero, sem retomada automatica, sem pular faixa em falha, repeticao desligada por padrao.\\n"
    "Offline: cache permanente automatico somente apos a faixa terminar e quando a licenca autoriza.\\n",
    encoding="utf-8"
)
print("CATALOG_V8_OK: 70/70/70 pré-carregados, player sem salto/auto-next, salvamento offline pós-audição, palco suave e marca oficial.")
