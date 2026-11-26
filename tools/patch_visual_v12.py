#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1]).resolve()
html_path = root / 'app/src/main/assets/rima-lab.html'
gradle_path = root / 'app/build.gradle'
html = html_path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global html
    if old not in html:
        if new in html:
            return
        raise SystemExit(f'V12_FAIL: trecho não encontrado: {label}')
    html = html.replace(old, new, 1)


# Rhyme families now use the stressed phonetic ending, not just written suffixes.
old_rhyme = """const RIMA_RICH_HINTS_V9={'TAÇA':['graça','raça','caça','massa'],'CONSOLE':['controle','descontrole','enrole','engole'],'POSTE':['goste','encoste','desgoste','aposte'],'MAREMOTO':['terremoto','remoto','moto','foto'],'BATIMENTO':['pensamento','lamento','talento','momento'],'LIMPAR':['poupar','disparar','preparar','escapar']};
const rimasDe=w=>{const exact=RIMA_RICH_HINTS_V9[String(w||'').toUpperCase()];if(exact)return shuf(exact).join(', ');const n=norm(w),f=RG.filter(x=>n.endsWith(norm(x[0]).slice(1))).sort((a,b)=>b[0].length-a[0].length)[0];if(!f)return'';return shuf(f[1].filter(x=>norm(x)!=n)).slice(0,4).join(', ')};"""
new_rhyme = r'''const RIMA_RICH_HINTS_V9={'TAÇA':['graça','raça','caça','massa'],'CONSOLE':['controle','descontrole','enrole','engole'],'POSTE':['goste','encoste','desgoste','aposte'],'MAREMOTO':['terremoto','remoto','moto','foto'],'BATIMENTO':['pensamento','lamento','talento','momento'],'LIMPAR':['poupar','disparar','preparar','escapar'],'DENÚNCIA':['renúncia','pronúncia','anúncia'],'MÉRITO':['pretérito','emérito','demérito']};
const rimaKeyV12=value=>{
 const words=String(value||'').toLowerCase().normalize('NFC').match(/[a-záàâãéêíóôõúç]+/g);
 if(!words||!words.length)return'';
 const word=words[words.length-1],chars=[...word];
 const marked=chars.findIndex(ch=>/[áàâãéêíóôõú]/.test(ch));
 let stress=marked;
 if(stress<0){
  const vowels='aeiouáàâãéêíóôõú',diphthongs=new Set(['ai','au','ei','eu','oi','ou','ui','ão','ãe','õe']);
  const nuclei=[];
  for(let i=0;i<chars.length;i++){
   if(!vowels.includes(chars[i]))continue;
   const pair=chars[i]+(chars[i+1]||'');
   if(i+1<chars.length&&vowels.includes(chars[i+1])&&diphthongs.has(pair)){nuclei.push(i);i++;}
   else nuclei.push(i);
  }
  if(!nuclei.length)return'';
  const paroxytone=/(?:[aeiouáàâãéêíóôõú]s?|am|em|ens)$/i.test(word);
  stress=nuclei.length>1&&paroxytone?nuclei[nuclei.length-2]:nuclei[nuclei.length-1];
 }
 return norm(chars.slice(stress).join(''));
};
const rimasDe=w=>{
 const exact=RIMA_RICH_HINTS_V9[String(w||'').toUpperCase()];
 if(exact)return shuf(exact).join(', ');
 const key=rimaKeyV12(w);if(!key)return'';
 const f=RG.filter(x=>norm(x[0]).slice(1)===key).sort((a,b)=>b[0].length-a[0].length)[0];
 if(!f)return'';
 return shuf(f[1].filter(x=>norm(x)!==norm(w)&&rimaKeyV12(x)===key)).slice(0,4).join(', ');
};'''
replace_once(old_rhyme, new_rhyme, 'correspondência fonética das rimas')

# The secondary hint overlay had a second, conflicting non-rhyming POSTE list.
replace_once("'POSTE':['teste','veste','agreste','nordeste'],",
             "'POSTE':['goste','encoste','desgoste','aposte'],\n  'DENUNCIA':['renúncia','pronúncia','anúncia'],\n  'MERITO':['pretérito','emérito','demérito'],",
             'dicas rápidas de rima')

# Stop the word entrance animation and give the beat halo enough time to appear.
replace_once("$('#cs').textContent=c.sub;stamp(w);WD.nw++",
             "$('#cs').textContent=c.sub;WD.nw++", 'animação de entrada da palavra')
replace_once("setTimeout(()=>e.classList.remove('hit'),210)",
             "setTimeout(()=>e.classList.remove('hit'),440)", 'duração da iluminação no pulso')

# Replace the old scaleX/nowrap fit script that lost to CSS !important rules.
start_tag = '<style id="rima-word-fit-v9">'
start = html.find(start_tag)
if start < 0:
    if 'rima-word-fit-v12' not in html:
        raise SystemExit('V12_FAIL: bloco antigo de ajuste de palavra não encontrado')
else:
    script_start = html.find('<script id="rima-word-fit-script-v9">', start)
    end = html.find('</script>', script_start)
    if script_start < 0 or end < 0:
        raise SystemExit('V12_FAIL: fim do script de ajuste de palavra não encontrado')
    end += len('</script>')
    fit_block = r'''<style id="rima-word-fit-v12">
#stg.stage #cb{display:block!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;margin:12px auto!important;padding:8px 6px!important;text-align:center!important;color:#edc34d!important;text-shadow:0 0 18px rgba(237,195,77,.16)!important;letter-spacing:-.045em!important;line-height:1.04!important;white-space:nowrap!important;word-break:normal!important;overflow-wrap:normal!important;hyphens:none!important;transform:none!important;animation:none!important;transition:none!important;filter:none!important;will-change:auto!important}
#stg.stage.hit #cb{color:#edc34d!important;transform:none!important;animation:none!important;filter:none!important}
</style>
<script id="rima-word-fit-script-v12">
(function(){
 const fit=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');if(!e||!stage)return;
  const raw=(e.textContent||'').trim();if(!raw)return;
  const available=Math.max(100,stage.clientWidth-54);
  const max=raw.length>18?92:raw.length>12?98:104;
  e.style.setProperty('white-space','nowrap','important');
  e.style.setProperty('word-break','normal','important');
  e.style.setProperty('overflow-wrap','normal','important');
  e.style.setProperty('transform','none','important');
  let low=20,high=max;
  for(let i=0;i<13;i++){
   const mid=(low+high)/2;
   e.style.setProperty('font-size',mid.toFixed(1)+'px','important');
   if(e.scrollWidth<=available)low=mid;else high=mid;
  }
  e.style.setProperty('font-size',Math.floor(low)+'px','important');
  if(e.scrollWidth>available){
   e.style.setProperty('white-space','normal','important');
   e.style.setProperty('overflow-wrap','anywhere','important');
   e.style.setProperty('font-size','25px','important');
  }
 };
 const boot=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');if(!e||!stage)return;
  new MutationObserver(fit).observe(e,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize',fit,{passive:true});
  fit();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>'''
    html = html[:start] + fit_block + html[end:]

# Final style override: stable gold type and a diffuse gold beat pulse around the stage.
visual_css = r'''<style id="rimalab-visual-v12">
:root{--ac:#edc34d!important;--hl:#edc34d!important}
#stg.stage{position:relative!important;border:1px solid rgba(237,195,77,.34)!important;box-shadow:0 0 0 1px rgba(237,195,77,.07),inset 0 0 24px rgba(237,195,77,.035)!important;transform:none!important;overflow:hidden!important}
#stg.stage.hit{border-color:rgba(255,218,112,.96)!important;box-shadow:0 0 0 1px rgba(237,195,77,.20),0 0 30px rgba(237,195,77,.25),inset 0 0 30px rgba(237,195,77,.095)!important;transform:none!important}
#stg.stage::after{content:""!important;display:block!important;position:absolute!important;inset:1px!important;z-index:4!important;pointer-events:none!important;border:1px solid rgba(237,195,77,.18)!important;border-radius:inherit!important;opacity:.22!important;box-shadow:inset 0 0 18px rgba(237,195,77,.06),0 0 10px rgba(237,195,77,.05)!important}
#stg.stage.hit::after{animation:rimalab-gold-pulse-v12 .44s ease-out!important}
#bt .stage{position:relative!important;transform:none!important}
#bt .stage::after{content:""!important;display:block!important;position:absolute!important;inset:1px!important;z-index:4!important;pointer-events:none!important;border:1px solid rgba(237,195,77,.18)!important;border-radius:inherit!important;opacity:.16!important;box-shadow:inset 0 0 16px rgba(237,195,77,.05)!important}
#bt .stage.hit{border-color:rgba(255,218,112,.96)!important;box-shadow:0 0 0 1px rgba(237,195,77,.18),0 0 26px rgba(237,195,77,.22),inset 0 0 24px rgba(237,195,77,.08)!important;transform:none!important}
#bt .stage.hit::after{animation:rimalab-gold-pulse-v12 .44s ease-out!important}
#rima-splash:before,#rima-splash:after{border-color:rgba(237,195,77,.16)!important}
@keyframes rimalab-gold-pulse-v12{0%{opacity:.95;border-color:rgba(255,224,142,.98)!important;box-shadow:inset 0 0 34px rgba(237,195,77,.22),0 0 34px rgba(237,195,77,.34)!important}100%{opacity:.18;border-color:rgba(237,195,77,.18)!important;box-shadow:inset 0 0 8px rgba(237,195,77,.025),0 0 6px rgba(237,195,77,.025)!important}}
#stg.stage #cb,.stage .word,#bt .stage .word{color:#edc34d!important;text-shadow:0 0 18px rgba(237,195,77,.15)!important;transform:none!important;animation:none!important;filter:none!important}
.rm span,#op .tag,#op .chip{background:rgba(237,195,77,.11)!important;border:1px solid rgba(237,195,77,.56)!important;color:#ffe4a0!important;box-shadow:inset 0 0 12px rgba(237,195,77,.035)!important}
.splash-mark{background:linear-gradient(145deg,#edc34d 0%,#d6a833 100%)!important;border:1px solid rgba(255,224,142,.85)!important;color:#17140d!important;box-shadow:0 0 34px rgba(237,195,77,.24),inset 0 1px rgba(255,255,255,.32)!important}
.splash-mark .splash-initial{display:block!important;position:relative!important;z-index:2!important;font-family:Anton,Impact,sans-serif!important;font-size:62px!important;font-weight:900!important;line-height:.9!important;color:#17140d!important;text-shadow:0 1px 0 rgba(255,255,255,.12)!important;transform:none!important;opacity:1!important}
.splash-mark .splash-initial::after{content:none!important}
@media(prefers-reduced-motion:reduce){#stg.stage.hit::after{animation:none!important;opacity:.24!important}}
</style>'''
if 'id="rimalab-visual-v12"' not in html:
    pos = html.lower().rfind('</body>')
    if pos < 0:
        raise SystemExit('V12_FAIL: </body> não encontrado para CSS final')
    html = html[:pos] + visual_css + '\n' + html[pos:]

# 0 ms is "not reported", not proof of no speaker delay. Preserve manual offset.
replace_once(
 'Opcional: toque em <b>Calibrar</b> para usar a latência informada pelo aparelho. Não precisa de microfone nem aumentar o volume.',
 'A leitura automática usa apenas a latência que o Android/WebView informa. Ela não mede o atraso físico de uma caixa Bluetooth. Se o sistema não informar o valor, o ajuste atual será preservado.',
 'explicação da calibração')
replace_once("<span class=\"lat-v\">'+LAT+'</span><small>ms</small>",
             "<span class=\"lat-v\">'+LAT+'</span><small>ms de ajuste</small>",
             'rótulo do valor de sincronização')
replace_once('Calibração automática pronta. O ajuste fino também pode ser feito pela barra.',
             'Ajuste manual: '+"'+LAT+'"+' ms. Leitura automática disponível quando o Android informa a latência.',
             'status inicial do calibrador')

cal_pattern = re.compile(r'async function cal\(\)\{.*?\}\n(?=const CH=)', re.S)
cal_match = cal_pattern.search(html)
if not cal_match:
    raise SystemExit('V12_FAIL: função cal() não encontrada')
new_cal = r'''async function cal(){if(CAL_RUN)return;const run={cancelled:false,timer:null,sources:new Set()};CAL_RUN=run;const ms=t=>$$('.cm').forEach(e=>e.textContent=t),start=$('#cal-start'),stopBtn=$('#cal-stop');if(start){start.disabled=true;start.textContent='Verificando saída...'}if(stopBtn)stopBtn.hidden=true;try{if(play)stop();ini();await ctx.resume();if(run.cancelled)return;const values=[];for(let i=0;i<9;i++){if(run.cancelled)return;const base=Number(ctx.baseLatency)||0,output=Number(ctx.outputLatency)||0,v=base+output;if(Number.isFinite(v)&&v>0&&v<=.3)values.push(v*1000);await new Promise(ok=>setTimeout(ok,60))}if(run.cancelled)return;values.sort((a,b)=>a-b);if(values.length){const measured=values[Math.floor(values.length/2)],md=Math.max(1,Math.min(300,Math.round(measured)));setLat(md);ms('Android/WebView informou aproximadamente '+md+' ms de latência interna. Isso não mede o atraso acústico adicional da caixa Bluetooth.')}else{ms('Latência não informada pelo Android/WebView. 0 ms não significa ausência de atraso. O ajuste atual foi preservado; para medir a caixa Bluetooth é necessário retorno de áudio (microfone/loopback).')} }catch(e){ms('Não foi possível ler a latência do sistema. O ajuste atual foi preservado; a barra continua disponível para compensação manual.')}finally{if(CAL_RUN===run)CAL_RUN=null;if(start){start.disabled=false;start.textContent='Calibrar (opcional)'}if(stopBtn)stopBtn.hidden=true}}'''
html = html[:cal_match.start()] + new_cal + '\n' + html[cal_match.end():]
html_path.write_text(html, encoding='utf-8')

# Increment the Android version so 2.9.4 installs over 2.9.3.
gradle = gradle_path.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+30\b', gradle):
    gradle = re.sub(r'\bversionCode\s+30\b', 'versionCode 31', gradle, count=1)
elif not re.search(r'\bversionCode\s+31\b', gradle):
    raise SystemExit('V12_FAIL: versionCode não é 30 nem 31')
if re.search(r"versionName\s+['\"]2\.9\.3['\"]", gradle):
    gradle = re.sub(r"versionName\s+['\"]2\.9\.3['\"]", "versionName '2.9.4'", gradle, count=1)
elif "versionName '2.9.4'" not in gradle:
    raise SystemExit('V12_FAIL: versionName não é 2.9.3 nem 2.9.4')
gradle_path.write_text(gradle, encoding='utf-8')
print('VISUAL_V12_OK: rimas fonéticas, palco responsivo, dourado, R do splash e calibração honesta')
