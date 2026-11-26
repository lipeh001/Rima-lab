#!/usr/bin/env python3
from pathlib import Path
import re, sys
root=Path(sys.argv[1]).resolve()
hp=root/"app/src/main/assets/rima-lab.html"
s=hp.read_text(encoding="utf-8")

# Simple, user-facing copy. No mention of licensing.
for old in [
 "Escolha um beat e toque em Ouvir. Depois de ouvir a faixa, o Rima Lab tenta guardá-la para reprodução offline quando a licença autoriza o armazenamento.",
 "Escolha uma base para ouvir e treinar. Ouça até o fim. Quando a licença permitir, o beat será salvo automaticamente para uso offline.",
 "Escolha uma base para ouvir e treinar. Depois de ouvir, você pode salvar o beat no celular para usar offline."
]:
 s=s.replace(old,"Escolha um beat para ouvir e treinar.")
s=s.replace("Fonte: catálogo Jamendo. Toque no nome do artista para consultar a faixa e sua licença.","Catálogo de instrumentais. Toque no artista para ver mais informações.")
if "Escolha um beat para ouvir e treinar." not in s: raise SystemExit("VISUAL_V10_FAIL: seletor")

# Device-native audio pipeline latency: no microphone, test tone or loud volume.
cal_html = """const calHTML=()=>'<section class="card calibrator-card"><div class="cal-top"><span class="cal-icon" aria-hidden="true">◉</span><div><h2>Sincronização</h2><p class="mut">Ajuste automático do áudio e do palco.</p></div></div><div class="cal-help"><p>Toque em <b>Calibrar automaticamente</b>. O app mede a latência de áudio informada pelo aparelho. Não precisa de microfone nem de aumentar o volume.</p></div><div class="cal-control"><div class="cal-value"><span class="lat-v">'+LAT+'</span><small>ms</small></div><input type="range" class="lat-s" min="0" max="1200" step="5" value="'+LAT+'" oninput="setLat(+this.value)" aria-label="Ajuste fino da sincronização"></div><div class="cal-actions"><button id="cal-start" class="btn w cal-button" onclick="cal()">Calibrar automaticamente</button><button id="cal-stop" class="btn g w cal-stop" onclick="calCancel()" hidden>Parar</button></div><p class="mut cm" role="status" aria-live="polite">Calibração automática pronta. O ajuste fino também pode ser feito pela barra.</p></section>';"""
s,n=re.subn(r"const calHTML=\(\)=>.*?</section>[\x60];",cal_html,s,count=1,flags=re.S)
if n!=1: raise SystemExit("VISUAL_V10_FAIL: calHTML")

cal_code = r"""async function cal(){if(CAL_RUN)return;const run={cancelled:false,timer:null,sources:new Set()};CAL_RUN=run;const ms=t=>$$('.cm').forEach(e=>e.textContent=t),start=$('#cal-start'),stopBtn=$('#cal-stop');if(start){start.disabled=true;start.textContent='Medindo áudio...'}if(stopBtn)stopBtn.hidden=true;try{if(play)stop();ini();await ctx.resume();if(run.cancelled)return;const values=[];for(let i=0;i<9;i++){if(run.cancelled)return;const v=Number(ctx.baseLatency);if(Number.isFinite(v)&&v>=0&&v<=1.2)values.push(v*1000);await new Promise(ok=>requestAnimationFrame(()=>ok()))}if(run.cancelled)return;values.sort((a,b)=>a-b);const measured=values.length?values[Math.floor(values.length/2)]:0;const md=Math.max(0,Math.min(1200,Math.round(measured/5)*5));setLat(md);const output=Math.max(0,Number(ctx.outputLatency)||0)*1000;ms(values.length?'Concluído: processamento '+md+' ms; saída do aparelho '+Math.round(output/5)*5+' ms. A sincronização foi atualizada.':'Sincronização automática ativada. O aparelho não informou latência extra; ajuste fino disponível na barra.')}catch(e){setLat(0);ms('Sincronização automática ativada com o relógio nativo do áudio. O ajuste fino está disponível na barra.')}finally{if(CAL_RUN===run)CAL_RUN=null;if(start){start.disabled=false;start.textContent='Calibrar automaticamente'}if(stopBtn)stopBtn.hidden=true}}"""
s,n=re.subn(r"async function cal\(\)\{.*?\}\nconst CH=",cal_code+"\nconst CH=",s,count=1,flags=re.S)
if n!=1: raise SystemExit("VISUAL_V10_FAIL: cal function")
s=s.replace("function setLat(v){LAT=v;LATSET=true;","function setLat(v){v=Math.max(0,Math.min(1200,+v||0));LAT=v;LATSET=true;")

style=r"""<style id="rima-visual-v10">
:root{--bg:#0b0b10!important;--card:#15151d!important;--card2:#1d1b27!important;--ink:#f4f0e7!important;--mut:#aaa5b4!important;--ac:#edc34d!important;--hl:#f4cf62!important;--ac2:#a58ae8!important;--ok:#72d7b5!important;--on:#17141c!important;--ln:rgba(237,195,77,.19)!important;--g1:#edc34d!important;--g2:#a58ae8!important;--g3:#c0a9ef!important;--glass:rgba(24,23,31,.88)!important;--gl:rgba(237,195,77,.16)!important;--ux-line:rgba(237,195,77,.18)!important;--ux-glow:rgba(165,138,232,.12)!important;color-scheme:dark}
html{background:#0b0b10!important}
body{background:radial-gradient(ellipse at 92% -12%,rgba(237,195,77,.12),transparent 44%),radial-gradient(ellipse at 0% 48%,rgba(165,138,232,.10),transparent 42%),#0b0b10!important;color:var(--ink)!important}
.hd h1{background:linear-gradient(100deg,#fff4d0 8%,#edc34d 52%,#a58ae8 100%)!important;-webkit-background-clip:text!important;background-clip:text!important}
.word{color:#f4cf62!important;text-shadow:0 0 20px rgba(237,195,77,.18)!important}
.card{border-color:rgba(237,195,77,.15)!important}
.btn:not(.g),button.on,.chip.on{background:linear-gradient(115deg,#edc34d,#d9ad3c)!important;color:#17141c!important;border-color:#edc34d!important;box-shadow:0 5px 18px rgba(237,195,77,.16)!important}
.btn.g{background:rgba(165,138,232,.055)!important;border:1px solid rgba(165,138,232,.35)!important;color:#e7defb!important;box-shadow:none!important}
nav{border-color:rgba(237,195,77,.18)!important;background:rgba(17,16,23,.97)!important}
nav button{color:#9993a5!important}
nav button.on{color:#f4cf62!important;background:rgba(237,195,77,.10)!important;box-shadow:none!important}
nav button.on::before{background:#edc34d!important}
#pbar{background:rgba(17,16,23,.98)!important;border-color:rgba(165,138,232,.30)!important;box-shadow:0 -8px 26px rgba(0,0,0,.42)!important}
#pbar button:not(.pws):not(.pwm){background:linear-gradient(135deg,#edc34d,#d9ad3c)!important;color:#17141c!important}
#pbar button.pws{border-color:rgba(165,138,232,.24)!important;color:#b7a4e8!important}
.pwp i,.pwp b{background:#edc34d!important}
.dots i.on{background:#edc34d!important;border-color:#edc34d!important;box-shadow:0 0 22px rgba(237,195,77,.28)!important}
.dots i:first-child.on{background:#a58ae8!important;border-color:#a58ae8!important;box-shadow:0 0 20px rgba(165,138,232,.25)!important}
.tag,.chip{border-color:rgba(165,138,232,.38)!important}
.calibrator-card .cal-icon{color:#edc34d!important}
.calibrator-card{border-color:rgba(165,138,232,.26)!important}
.calibrator-card .lat-s{accent-color:#edc34d!important}
.dlb.ok{background:#72d7b5!important;border-color:#72d7b5!important}
.splash-mark,.splash-loader i,.splash-progress i{border-color:#edc34d!important;background:#edc34d!important;color:#edc34d!important}
.splash-mark span{color:#a58ae8!important}
@media (orientation:landscape) and (max-height:850px){
 nav{display:none!important;visibility:hidden!important;pointer-events:none!important}
 #pbar{display:flex!important;left:8px!important;right:8px!important;bottom:calc(7px + env(safe-area-inset-bottom,0px))!important;width:auto!important;max-width:none!important;height:50px!important;min-height:50px!important;margin:0!important;border-radius:15px!important;z-index:150!important}
 body.pl main{padding-bottom:calc(66px + env(safe-area-inset-bottom,0px))!important}
 #lv:not([hidden]){padding-bottom:0!important}
}
@media (orientation:portrait){
 nav{display:grid!important;visibility:visible!important;pointer-events:auto!important}
 #pbar{bottom:calc(72px + env(safe-area-inset-bottom,0px))!important}
}
@media(prefers-reduced-motion:reduce){#stg.stage.hit::after{animation:none!important}}
</style>"""
if 'id="rima-visual-v10"' not in s:s=s.replace("</head>",style+"\n</head>",1)
else: raise SystemExit("VISUAL_V10_FAIL: style already applied")

s=s.replace("rimalab-verified-instrumental-v4-20261125","rimalab-verified-instrumental-v10")
s=s.replace("rimalab-preloaded-70-each-v8","rimalab-preloaded-verified-instrumental-v10")
hp.write_text(s,encoding="utf-8")

gp=root/"app/build.gradle"
g=gp.read_text(encoding="utf-8")
if "versionCode 28" in g:g=g.replace("versionCode 28","versionCode 29",1)
elif "versionCode 29" not in g:raise SystemExit("VISUAL_V10_FAIL: versionCode 28")
if "versionName '2.9.1'" in g:g=g.replace("versionName '2.9.1'","versionName '2.9.2'",1)
elif "versionName '2.9.2'" not in g:raise SystemExit("VISUAL_V10_FAIL: versionName 2.9.1")
gp.write_text(g,encoding="utf-8")
print("VISUAL_V10_OK")
