#!/usr/bin/env python3
from pathlib import Path
import re, sys
root=Path(sys.argv[1]).resolve()
assets=root/'app/src/main/assets'
hp=assets/'rima-lab.html'
s=hp.read_text(encoding='utf-8')

# Calibragem opcional, baseada apenas na latência reportada pelo próprio AudioContext.
s=s.replace('max="1200" step="5"','max="300" step="1"')
s=s.replace('Math.min(1200,Math.round(measured/5)*5)','Math.min(300,Math.round(measured))')
s=s.replace('Math.min(1200,+v||0)','Math.min(300,+v||0)')
s=s.replace('for(let i=0;i<9;i++){if(run.cancelled)return;const v=Number(ctx.baseLatency);if(Number.isFinite(v)&&v>=0&&v<=1.2)values.push(v*1000);',
'''for(let i=0;i<9;i++){if(run.cancelled)return;const base=Number(ctx.baseLatency)||0,output=Number(ctx.outputLatency)||0,v=base+output;if(Number.isFinite(v)&&v>=0&&v<=.3)values.push(v*1000);''')
s=s.replace("const output=Math.max(0,Number(ctx.outputLatency)||0)*1000;ms(values.length?'Concluído: processamento '+md+' ms; saída do aparelho '+Math.round(output/5)*5+' ms. A sincronização foi atualizada.':'Sincronização automática ativada. O aparelho não informou latência extra; ajuste fino disponível na barra.')",
"ms(values.length?'Concluído: latência do aparelho '+md+' ms. Sincronização atualizada.':'O aparelho não informou latência extra. Sincronização automática ativa; ajuste fino disponível na barra.')")
s=s.replace('Calibrar automaticamente</button>','Calibrar (opcional)</button>')
s=s.replace("start.textContent='Calibrar automaticamente'","start.textContent='Calibrar (opcional)'")
s=s.replace('Ajuste automático do áudio e do palco.','Ajuste opcional da latência do aparelho.')
s=s.replace('Toque em <b>Calibrar automaticamente</b>. O app mede a latência de áudio informada pelo aparelho. Não precisa de microfone nem de aumentar o volume.','Opcional: toque em <b>Calibrar</b> para usar a latência informada pelo aparelho. Não precisa de microfone nem aumentar o volume.')
s=s.replace('Calibrar automaticamente pronta. O ajuste fino também pode ser feito pela barra.','Calibração opcional. O ajuste fino também pode ser feito pela barra.')

# A navegação inferior some em paisagem; o seekbar permanece acessível no dock horizontal.
land='''@media (orientation:landscape) and (max-height:850px){
 #pbar{height:72px!important;min-height:72px!important;padding-bottom:15px!important;position:fixed!important}
 #pbar .pwscr{display:flex!important;visibility:visible!important;position:absolute!important;left:14px!important;right:14px!important;bottom:4px!important;height:8px!important;min-height:8px!important;z-index:4!important;align-items:center!important}
 #pbar .pwscr input[type=range],#pbar .pwscr input{display:block!important;visibility:visible!important;width:100%!important;min-width:0!important;height:6px!important;opacity:1!important;pointer-events:auto!important;accent-color:#edc34d!important}
 #pbar .pwinfo{display:none!important}
}
'''
if 'id="rima-landscape-seekbar-v11"' not in s:
 s=s.replace('</style>','</style><style id="rima-landscape-seekbar-v11">'+land+'</style>',1)

# Tira da lista o item reportado, inclusive se já estiver no cache local antigo.
if 'rima-filter-nonbeat-v11' not in s:
 anchor='function zBuild(st){'
 if anchor not in s: raise SystemExit('V11_FAIL: zBuild')
 s=s.replace(anchor,"function rimaIsBlockedBeatV11(x){const t=String(Array.isArray(x)?x[1]:(x&&x.name)||'').toLowerCase();return /rap\\s+boom\\s+bap\\s+gritty\\s+old\\s+school/.test(t)}\n"+anchor,1)
 s=s.replace("for(const x of (RIMA_CATALOG_SEED_V8[st]||[])){if(!x||seen.has(String(x[4])))continue;",
 "for(const x of (RIMA_CATALOG_SEED_V8[st]||[])){if(!x||rimaIsBlockedBeatV11(x)||seen.has(String(x[4])))continue;",1)
 s=s.replace("if(L.length<cap&&m&&m[5]===st&&(ZDL[k]||ZLOCAL.has(k))&&!seen.has(String(m[4])))",
 "if(L.length<cap&&m&&m[5]===st&&!rimaIsBlockedBeatV11(m)&&(ZDL[k]||ZLOCAL.has(k))&&!seen.has(String(m[4])))",1)
 s=s.replace("for(const x of (ZRAW[st]||[])){if(L.length>=cap)break;if(!x||seen.has(String(x[4])))continue;",
 "for(const x of (ZRAW[st]||[])){if(L.length>=cap)break;if(!x||rimaIsBlockedBeatV11(x)||seen.has(String(x[4])))continue;",1)
 s=s.replace("rimalab-preloaded-verified-instrumental-v10","rimalab-preloaded-verified-instrumental-v11")
 # Keep this version bump even if the old literal differs.
 s=s.replace("rimalab-preloaded-70-each-v8","rimalab-preloaded-verified-instrumental-v11")

# Notification large icon: same R, now gold instead of green.
service_path=root/'app/src/main/java/app/rimalab/MusicService.java'
service=service_path.read_text(encoding='utf-8')
service=service.replace('p.setColor(0xFFD7FB57)','p.setColor(0xFFEDC34D)')
service=service.replace('p.setColor(0xFFd7fb57)','p.setColor(0xFFEDC34D)')
service_path.write_text(service,encoding='utf-8')

# Android update version.
gp=root/'app/build.gradle'
g=gp.read_text(encoding='utf-8')
g=re.sub(r'versionCode\\s+29\\b','versionCode 30',g,count=1)
g=g.replace("versionName '2.9.2'","versionName '2.9.3'",1)
if 'versionCode 30' not in g or "versionName '2.9.3'" not in g: raise SystemExit('V11_FAIL: versão')
gp.write_text(g,encoding='utf-8')
hp.write_text(s,encoding='utf-8')
print('VISUAL_V11_OK')
