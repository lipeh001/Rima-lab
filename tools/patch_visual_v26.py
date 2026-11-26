#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# 1) Voltar: remove o excesso de margem adicionado no v25.
css=r"""<style id="rimalab-final-polish-v26">
#lv:not([hidden])>.bk{
 margin-top:0!important;margin-bottom:8px!important;
 align-self:flex-start!important;position:relative!important;top:0!important;
}
#lv:not([hidden]) #stg.stage #cb{
 box-sizing:border-box!important;width:100%!important;max-width:100%!important;
 padding:8px 6px!important;line-height:1.08!important;
 font-size:128px!important;white-space:nowrap!important;
 word-break:normal!important;overflow-wrap:normal!important;
}
@media (orientation:landscape) and (max-height:850px){
 #pbar{
  position:fixed!important;top:auto!important;
  bottom:calc(8px + env(safe-area-inset-bottom,0px))!important;
  left:10px!important;right:10px!important;
  transform:none!important;margin:0!important;
  height:64px!important;min-height:64px!important;
  z-index:80!important;
 }
 body.pl main{padding-bottom:calc(86px + env(safe-area-inset-bottom,0px))!important}
 #lv:not([hidden]) #stg.stage{max-height:calc(100svh - 112px)!important}
}
</style>"""
if 'id="rimalab-final-polish-v26"' not in h:
 pos=h.lower().rfind('</body>')
 if pos<0:raise SystemExit('V26_FAIL: body não encontrado')
 h=h[:pos]+css+'\n'+h[pos:]

# 2) Fonte principal: volta a ter presença; reduz somente quando a palavra realmente não cabe.
fit=r"""<script id="rimalab-word-fit-v26">
(function(){
 const fit=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!e||!stage||!e.textContent.trim())return;
  const available=Math.max(80,stage.clientWidth-52);
  const maxHeight=Math.max(48,Math.min(stage.clientHeight*.38,190));
  const measure=()=>{
   try{const r=document.createRange();r.selectNodeContents(e);const b=r.getBoundingClientRect();return {w:b.width,h:b.height}}
   catch(_){return {w:e.scrollWidth,h:e.getBoundingClientRect().height}}
  };
  let low=38,high=128;
  e.style.setProperty('font-size','128px','important');
  for(let i=0;i<16;i++){
   const mid=(low+high)/2;e.style.setProperty('font-size',mid.toFixed(1)+'px','important');
   const b=measure();if(b.w<=available&&b.h<=maxHeight)low=mid;else high=mid;
  }
  e.style.setProperty('font-size',Math.floor(low)+'px','important');
 };
 const boot=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');if(!e||!stage)return;
  new MutationObserver(fit).observe(e,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize',fit,{passive:true});
  window.addEventListener('orientationchange',()=>setTimeout(fit,120),{passive:true});
  fit();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>"""
if 'id="rimalab-word-fit-v26"' not in h:
 pos=h.lower().rfind('</body>');h=h[:pos]+fit+'\n'+h[pos:]

# 3) Calibrador: deixa de fingir que mede a latência. O botão emite pulsos pela caixa Bluetooth
# para a pessoa ajustar a compensação manual até o palco e o beat coincidirem.
cal=r"""async function cal(){
 if(CAL_RUN)return;
 CAL_RUN=true;
 const start=$('#cal-start'),stopBtn=$('#cal-stop');
 const ms=t=>$$('.cm').forEach(e=>e.textContent=t);
 if(start){start.disabled=true;start.textContent='Testando...'}
 if(stopBtn)stopBtn.hidden=true;
 let ctx=null;
 try{
  const AC=window.AudioContext||window.webkitAudioContext;
  if(!AC)throw new Error('AudioContext indisponível');
  ctx=new AC();await ctx.resume();
  ms('Ouça os pulsos na caixa Bluetooth. Ajuste a barra até eles coincidirem com a batida do palco.');
  const t=ctx.currentTime+.18;
  for(let i=0;i<6;i++){
   const at=t+i*.55,osc=ctx.createOscillator(),gain=ctx.createGain();
   osc.type='sine';osc.frequency.value=880;
   gain.gain.setValueAtTime(.0001,at);
   gain.gain.exponentialRampToValueAtTime(.22,at+.008);
   gain.gain.exponentialRampToValueAtTime(.0001,at+.075);
   osc.connect(gain);gain.connect(ctx.destination);
   osc.start(at);osc.stop(at+.085);
  }
  await new Promise(resolve=>setTimeout(resolve,3600));
  ms('Teste concluído. Se ainda houver diferença, ajuste a barra até a batida do palco coincidir com o beat.');
 }catch(e){
  ms('Não foi possível tocar o teste. Confira o volume da caixa Bluetooth e ajuste a barra manualmente.');
 }finally{
  if(ctx)try{await ctx.close()}catch(e){}
  CAL_RUN=false;
  if(start){start.disabled=false;start.textContent='Calibrar (opcional)'}
  if(stopBtn)stopBtn.hidden=true;
 }
}"""
h,n=re.subn(r"async function cal\(\)\{[\s\S]*?\}\s*const CH=",cal+"\nconst CH=",h,count=1)
if n!=1:
 # Some source variants use function cal without async.
 h,n=re.subn(r"function cal\(\)\{[\s\S]*?\}\s*const CH=",cal+"\nconst CH=",h,count=1)
if n!=1:raise SystemExit('V26_FAIL: não localizei a função cal()')

# Copy curto e sem explicação técnica.
repls={
 'A leitura automática usa apenas a latência que o Android/WebView informa. Ela não mede o atraso físico de uma caixa Bluetooth. Se o sistema não informar o valor, o ajuste atual será preservado.':'Use Calibrar com uma caixa Bluetooth para ouvir os pulsos de teste. Ajuste a barra até o palco e o beat ficarem sincronizados.',
 'Ajuste opcional da latência do aparelho.':'Use somente com uma caixa de som Bluetooth.',
 'Saída pelo alto-falante do celular: 0 ms de compensação. O Android/WebView não consegue medir automaticamente o atraso acústico nem identificar com segurança uma caixa Bluetooth. Se ouvir atraso, use o ajuste manual.':'Conecte uma caixa Bluetooth, toque em Calibrar e ajuste a barra até o palco acompanhar o beat.'
}
for a,b in repls.items():h=h.replace(a,b)

# 4) Pausa real: não continuar os pulsos visuais quando o player está pausado.
pulse_anchor='function pulse(q){'
if pulse_anchor not in h:raise SystemExit('V26_FAIL: pulse(q) não encontrado')
if 'if(typeof zPL!=="undefined"&&!zPL)return;' not in h:
 h=h.replace(pulse_anchor,pulse_anchor+'if(typeof zPL!=="undefined"&&!zPL)return;',1)

# 5) Retorno do app: só retoma WebAudio se o beat estava tocando; reativa o pulso do palco.
life=r"""<script id="rimalab-audio-lifecycle-v26">
(function(){
 let last=0;
 const resume=()=>{
  const now=Date.now();if(now-last<350)return;last=now;
  try{
   if(typeof zPL!=='undefined'&&!zPL)return;
   const contexts=[];
   for(const k of Object.keys(window)){
    let v;try{v=window[k]}catch(e){}
    if(v&&v&&typeof v==='object'&&typeof v.resume==='function'&&v.state==='suspended'&&typeof v.currentTime==='number')contexts.push(v);
   }
   Promise.all(contexts.map(c=>{try{return c.resume()}catch(e){return Promise.resolve()}})).then(()=>{
    if(typeof zPL!=='undefined'&&!zPL)return;
    if(typeof rimaPulseStageFrame==='function')rimaPulseStageFrame();
    if(typeof rimaPulseStageWord==='function')rimaPulseStageWord();
    if(typeof zMedia==='function')zMedia(true);
   });
  }catch(e){}
 };
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)resume()});
 window.addEventListener('pageshow',resume);
 window.addEventListener('focus',resume);
})();
</script>"""
if 'id="rimalab-audio-lifecycle-v26"' not in h:
 pos=h.lower().rfind('</body>');h=h[:pos]+life+'\n'+h[pos:]

hp.write_text(h,encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+45\b',g):g=re.sub(r'\bversionCode\s+45\b','versionCode 46',g,count=1)
elif not re.search(r'\bversionCode\s+46\b',g):raise SystemExit('V26_FAIL: versionCode inesperado')
if "versionName '3.0.3'" in g:g=g.replace("versionName '3.0.3'","versionName '3.0.4'",1)
elif "versionName '3.0.4'" not in g:raise SystemExit('V26_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('V26_OK: margem do voltar reduzida; player horizontal rebaixado; palavra ampliada e adaptativa; teste Bluetooth audível; pausa e retorno do áudio tratados')
