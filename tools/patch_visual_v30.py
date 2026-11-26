#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve(); hp=root/'app/src/main/assets/rima-lab.html'; gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
old="const MD3=[['pal','Palavras','Uma palavra por vez, com dica de como usar.'],['atq','Batalhar contra o app','Configure rounds, beat e duração da sua resposta em segundos ou compassos.'],['lig','Ligar duas palavras',''],['troc','Trocadilhos','Palavras com dois sentidos.'],['rima','Rimas em cadeia','Um som e uma sequência de rimas.'],['des','Desafios','Regras malucas pra soltar a criatividade.']];"
new="const MD3=[['pal','Palavras','Uma palavra por vez, com dica de como usar.'],['lig','Ligar duas palavras','Conecte duas ideias e crie uma ligação original entre elas.'],['troc','Trocadilhos','Palavras com dois sentidos.'],['rima','Rimas em cadeia','Um som e uma sequência de rimas.'],['des','Desafios','Regras malucas pra soltar a criatividade.']];"
if old not in h: raise SystemExit('V30_FAIL: lista MD3 não encontrada')
h=h.replace(old,new,1)
if "let mode='atq',nb4=4,fmt='norm';" in h:h=h.replace("let mode='atq',nb4=4,fmt='norm';","let mode='pal',nb4=4,fmt='norm';",1)
elif "let mode='pal',nb4=4,fmt='norm';" not in h:raise SystemExit('V30_FAIL: modo inicial não encontrado')
css="""<style id="rimalab-mode-config-v30">
#rima-v29-mode-banner{display:block!important;box-sizing:border-box!important;width:100%!important;margin:7px 0 9px!important;padding:13px 15px!important;border-radius:16px!important;border:1px solid rgba(224,190,76,.34)!important;background:linear-gradient(115deg,rgba(225,187,65,.13),rgba(19,27,19,.96) 62%)!important;box-shadow:inset 3px 0 0 #e8c45c!important}
#rima-v29-mode-banner:before{content:"1 · MODO ESCOLHIDO";display:block;margin:0 0 5px;color:#d8bd65;font-size:10px;font-weight:850;letter-spacing:.15em}
#rima-v29-mode-banner strong{font-size:17px!important;letter-spacing:.07em!important;line-height:1.25!important}
#rima-v29-mode-banner p{font-size:12px!important;line-height:1.4!important;margin:4px 0 0!important}
#rima-v29-mode-toggle{margin:0 0 9px!important}
#rima-v29-mode-list.open{max-height:2000px!important;overflow:visible!important;padding-bottom:8px!important}
#rima-v29-mode-list .mc{min-height:72px!important;height:auto!important;white-space:normal!important}
#rima-v29-mode-list .mc b,#rima-v29-mode-list .mc small{display:block!important;white-space:normal!important;overflow:visible!important;text-overflow:clip!important}
#rima-v29-mode-list .mc small{line-height:1.4!important;margin-top:5px!important}
@media(max-width:390px){#rima-v29-mode-banner{padding:12px!important}#rima-v29-mode-banner strong{font-size:16px!important}}
</style>"""
runtime="""<script id="rimalab-mode-config-runtime-v30">
(function(){const $=s=>document.querySelector(s);function arrange(){const step=$('#train-step-2');if(!step)return;const heading=step.querySelector('.stp'),banner=$('#rima-v29-mode-banner'),toggle=$('#rima-v29-mode-toggle'),list=$('#rima-v29-mode-list'),dfw=$('#dfw'),bp=$('#bp');if(heading){const h=heading.querySelector('h2');if(h)h.textContent='Escolha seu modo'}if(banner&&heading&&banner.previousElementSibling!==heading)heading.insertAdjacentElement('afterend',banner);if(banner&&toggle&&banner.nextElementSibling!==toggle)banner.insertAdjacentElement('afterend',toggle);if(toggle&&list&&toggle.nextElementSibling!==list)toggle.insertAdjacentElement('afterend',list);if(dfw){const n=dfw.querySelector('.stp .n'),t=dfw.querySelector('.stp h2');if(n)n.textContent='2';if(t)t.textContent='Dificuldade'}if(bp){const head=bp.previousElementSibling;if(head&&head.classList.contains('stp')){const n=head.querySelector('.n'),t=head.querySelector('h2');if(n)n.textContent='3';if(t)t.textContent='Escolha o beat'}}if(list){list.style.maxHeight=list.classList.contains('open')?'2000px':'0';list.style.overflow='visible'}}function init(){arrange();const step=$('#train-step-2');if(step)new MutationObserver(()=>requestAnimationFrame(arrange)).observe(step,{childList:true,subtree:true});const mode=$('#md');if(mode)new MutationObserver(()=>setTimeout(arrange,30)).observe(mode,{childList:true,subtree:true});document.addEventListener('click',e=>{if(e.target.closest('#rima-v29-mode-toggle,#rima-v29-mode-list [data-mode]'))setTimeout(arrange,35)});window.addEventListener('resize',arrange,{passive:true})}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init()})();
</script>"""
if 'id="rimalab-mode-config-v30"' not in h:
 p=h.lower().rfind('</body>');h=h[:p]+css+'\n'+h[p:]
if 'id="rimalab-mode-config-runtime-v30"' not in h:
 p=h.lower().rfind('</body>');h=h[:p]+runtime+'\n'+h[p:]
g=gp.read_text(encoding='utf-8');m=re.search(r'\\bversionCode\\s+(\\d+)',g)
if not m:raise SystemExit('V30_FAIL: versionCode ausente')
if int(m.group(1))<52:g=g[:m.start(1)]+'52'+g[m.end(1):]
m=re.search(r"versionName\\s+['\\"]([^'\\"]+)['\\"]",g)
if not m:raise SystemExit('V30_FAIL: versionName ausente')
if m.group(1)<'3.1.0':g=g[:m.start(1)]+'3.1.0'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V30_OK: lista de modos corrigida, modo integrado à configuração, etapas 1-2-3 e lista expansível; versão 3.1.0')
