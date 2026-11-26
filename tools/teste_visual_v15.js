#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const p=h.indexOf('function pulse(q){'),e=h.indexOf('function start()',p),pulse=p>=0?h.slice(p,e>p?e:p+2500):'';
const c=h.indexOf('async function cal(){'),ce=h.indexOf('const CH=',c),cal=c>=0?h.slice(c,ce>c?ce:c+2000):'';
const checks=[
 ['pulso do palco é disparado pela função pulse do relógio de áudio',pulse.includes("const stage=$('#lv').hidden?null:$('#stg')")&&pulse.includes("e.classList.add('hit')")],
 ['palavra e moldura recebem o mesmo tick e são rearmadas a cada batida',pulse.includes("word.classList.add('beat-word-hit')")&&pulse.includes("e.classList.remove('hit');void e.offsetWidth;e.classList.add('hit')")],
 ['efeito dourado forte recuperado na moldura',h.includes('rimalab-frame-impact-v15')&&h.includes('0 0 38px rgba(237,195,77,.38)')],
 ['palavra recebe impacto visual com brilho e escala',h.includes('rimalab-word-impact-v15')&&h.includes('scale(1.055)')],
 ['fonte base 112 px e só reduz por largura real do texto',h.includes("font-size:112px!important")&&h.includes("e.style.setProperty('font-size','112px','important')")&&h.includes('if(measure()<=available)return')],
 ['calibração não confunde latência interna do WebView com atraso acústico',cal.includes('setLat(0)')&&!cal.includes('ctx.baseLatency')&&!cal.includes('ctx.outputLatency')],
 ['calibração informa limite e mantém ajuste manual',cal.includes('use o ajuste manual')&&cal.includes('Calibrar (opcional)')],
 ['compensação antiga auto-inferida é zerada uma vez',h.includes('rimalab_lat_reset_v2')&&h.includes("localStorage.removeItem('lat')")],
 ['APK atualizado para 2.9.7 / versionCode 34',g.includes('versionCode 34')&&g.includes("versionName '2.9.7'")]
];
let bad=0;for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V15');
process.exit(bad?1:0);
