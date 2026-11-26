#!/usr/bin/env python3
from pathlib import Path
import sys,re
root=Path(sys.argv[1]).resolve()
h=root/'app/src/main/assets/rima-lab.html'
s=h.read_text(encoding='utf-8')
def rep(a,b,label):
 global s
 if a in s:s=s.replace(a,b,1)
 elif b not in s:raise SystemExit('QUALITY_V9_FAIL: '+label)
rep('Escolha uma base para ouvir e treinar. Ouça até o fim. Quando a licença permitir, o beat será salvo automaticamente para uso offline.','Escolha um beat e toque em Ouvir. Depois de ouvir a faixa, o Rima Lab tenta guardá-la para reprodução offline quando a licença autoriza o armazenamento.','texto do seletor')
rep("if(m=='pal'){const w=nW(),r=rimasDe(w);return{k:'Palavra de '+cat(w).toLowerCase(),big:w,sub:r&&Math.random()<.5?'Rimas possíveis: '+r:nP()}}","if(m=='pal'){let w=nW(),r=rimasDe(w),tries=0;while(!r&&tries++<24){w=nW();r=rimasDe(w)}if(!r){w='coração';r='razão, paixão, canção, ilusão'}return{k:'Palavra de '+cat(w).toLowerCase(),big:w,sub:'Rimas possíveis: '+r}}",'modo palavras')
# Famílias adicionais de rimas para palavras que antes não tinham sugestões.
rg=';oz:voz veloz atroz feroz algoz;ai:vai cai sai trai;ei:rei lei sei achei gritei cantei mandei;ouco:pouco louco rouco troco'
extra=';aça:taça cachaça fumaça carcaça couraça;ole:console controle descontrole enrole engole;oste:poste encoste aposte coste;oto:maremoto terremoto remoto devoto garoto piloto'
if ';aça:taça cachaça fumaça carcaça couraça' not in s:
 if rg not in s:raise SystemExit('QUALITY_V9_FAIL: famílias de rima')
 s=s.replace(rg,rg+extra,1)
old="function show(){rm.textContent='';if(!on)return;const t=($('#cb').textContent||'').trim();if(!t||/[\\s+]/.test(t)||t.includes('...'))return;build();const l=(IX.get(kk(t))||[]).filter(w=>w!=t.toLowerCase());if(!l.length)return;const p=shuf(l.slice()).slice(0,4);p.forEach(w=>{const s=document.createElement('span');s.textContent=w;rm.appendChild(s)})}"
new="function show(){rm.textContent='';if(!on)return;const t=($('#cb').textContent||'').trim();if(!t||/[\\s+]/.test(t)||t.includes('...'))return;const family=rimasDe(t);if(!family)return;const l=[...new Set(family.split(',').map(x=>x.trim()).filter(Boolean))];if(l.length<2)return;l.slice(0,4).forEach(w=>{const e=document.createElement('span');e.textContent=w;rm.appendChild(e)})}"
rep(old,new,'dicas fonéticas')
# Explicit rhyme families fix the exact examples reported in the screenshots.
rhymes="/* rima-rich-hints-v9 */\nconst RIMA_RICH_HINTS_V9={'TAÇA':['cachaça','fumaça','carcaça','couraça'],'CONSOLE':['controle','descontrole','enrole','engole'],'POSTE':['teste','veste','agreste','nordeste'],'MAREMOTO':['terremoto','remoto','devoto','garoto'],'BATIMENTO':['pensamento','lamento','talento','momento'],'LIMPAR':['poupar','disparar','preparar','escapar']};\n"
if 'RIMA_RICH_HINTS_V9' not in s:
 a='const rimasDe=w=>{'
 if a not in s:raise SystemExit('QUALITY_V9_FAIL: função rimasDe')
 s=s.replace(a,rhymes+"const rimasDe=w=>{const exact=RIMA_RICH_HINTS_V9[String(w||'').toUpperCase()];if(exact)return shuf(exact).join(', ');",1)

rep('Escolha uma base para ouvir e treinar. Na primeira vez que você ouvir, o app tenta salvar o beat automaticamente para ouvir offline, quando a licença permite.','Escolha um beat e toque em Ouvir. Depois de ouvir a faixa, o Rima Lab tenta guardá-la para reprodução offline quando a licença autoriza o armazenamento.','texto alternativo')
s=s.replace("const NAMES=['baixinho','médio','mais alto'],GAINS=[.3,.6,1],N=8,W=2","const NAMES=['volume confortável'],GAINS=[.18],N=7,W=1")
s=s.replace('T+i*.75','T+i*1.25').replace('t0+.75-off0','t0+1.25-off0').replace('ts[N+W-1]+1,w0=Date.now()','ts[N+W-1]+1.4,w0=Date.now()')
s=s.replace('for(let r=0;r<3;r++)','for(let r=0;r<1;r++)')
s=s.replace('if(mx>=.1&&mx>=rr*5)','if(mx>=.07&&mx>=rr*4)')
s=s.replace('if(o.res.length>=4){const a=[...o.res].sort((x,y)=>x-y),md=a[a.length>>1],ok=a.filter(x=>Math.abs(x-md)<=12);if(ok.length>=4){fin={ms:ok.reduce((u,v)=>u+v,0)/ok.length,n:ok.length};break}}','if(o.res.length>=5){const a=[...o.res].sort((x,y)=>x-y),md=a[a.length>>1],ok=a.filter(x=>Math.abs(x-md)<=10);if(ok.length>=5){const b=ok.sort((x,y)=>x-y),median=b[b.length>>1];fin={ms:Math.round(median/5)*5,n:ok.length};break}}')
s=s.replace('const md=Math.max(0,Math.min(600,Math.round(fin.ms)));','const md=Math.max(0,Math.min(1200,Math.round(fin.ms/5)*5));')
s=s.replace('dl<800','dl<1200')
s=s.replace('min="0" max="600" step="1"','min="0" max="1200" step="1"')
s=s.replace('O microfone não recebeu sinal. Confira a permissão, o volume e se outro app está usando o microfone.','O microfone não detectou o sinal de calibração. Confira a permissão e tente novamente em um local silencioso.')
s=s.replace('Não consegui detectar os sinais.','Não consegui isolar os sinais do ambiente.')
s=s.replace('<span class="cal-icon" aria-hidden="true">◷</span>','<span class="cal-icon" aria-hidden="true">🔔</span>')
s=s.replace("setTimeout(()=>e.classList.remove('hit'),145)","setTimeout(()=>e.classList.remove('hit'),210)")
old="const dl=Math.max(0,(t-ctx.currentTime)*1000)+LAT+((ctx.outputLatency||0)*1000);"
new="const zPerf=()=>{try{const q=ctx.getOutputTimestamp&&ctx.getOutputTimestamp();if(q&&q.contextTime>0&&q.performanceTime>0)return q.performanceTime+(t-q.contextTime)*1000}catch(e){}return performance.now()+(t-ctx.currentTime)*1000+((ctx.outputLatency||0)*1000)};const dl=Math.max(0,zPerf()-performance.now()+LAT);"
rep(old,new,'sincronização com relógio de saída')
style='<style id="rima-quality-v9">.bk{display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important}#train-step-2 .bk,#train-step-1 .bk,#lv .bk,#bt .bk{justify-content:center!important;text-align:center!important}#stg.stage.hit{border-color:rgba(225,255,105,.98)!important;box-shadow:0 0 0 2px rgba(215,251,87,.24),0 0 34px rgba(215,251,87,.42),inset 0 0 36px rgba(215,251,87,.16)!important;transform:scale(1.008)!important}#stg.stage.hit::after{content:""!important;display:block!important;position:absolute!important;inset:1px!important;border:1px solid rgba(230,255,135,.8)!important;border-radius:inherit!important;pointer-events:none!important;opacity:.9!important;animation:rl-quality-edge-v9 .34s ease-out!important}#bt .stage.hit{border-color:rgba(225,255,105,.96)!important;box-shadow:0 0 0 1px rgba(215,251,87,.2),0 0 28px rgba(215,251,87,.32),inset 0 0 30px rgba(215,251,87,.13)!important}@keyframes rl-quality-edge-v9{0%{opacity:1;box-shadow:inset 0 0 34px rgba(215,251,87,.25),0 0 34px rgba(215,251,87,.4)}100%{opacity:.12;box-shadow:inset 0 0 6px rgba(215,251,87,.03),0 0 4px rgba(215,251,87,.02)}}</style>'
if 'id="rima-quality-v9"' not in s:s=s.replace('</head>',style+'\n</head>',1)
h.write_text(s,encoding='utf-8')
icon=root/'app/src/main/res/drawable/ic_stat_beat.xml'
icon.write_text('<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="#FFFFFF" android:pathData="M4,10h2v8H4zM8,6h2v12H8zM12,3h2v15h-2zM16,8h2v10h-2zM20,11h2v7h-2z"/></vector>',encoding='utf-8')
gpath=root/'app/build.gradle'
g=gpath.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+27\b','versionCode 28',g).replace("versionName '2.9.0'","versionName '2.9.1'")
if 'versionCode 28' not in g or "versionName '2.9.1'" not in g:raise SystemExit('QUALITY_V9_FAIL: versão Gradle inesperada')
gpath.write_text(g,encoding='utf-8')
print('QUALITY_V9_OK')
