#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const p=h.indexOf('function pulse(q){'),e=h.indexOf('\n',p),pulse=p>=0?h.slice(p,e>p?e:p+1800):'';
const checks=[
 ['pulso do texto é acionado dentro da mesma função pulse() da moldura',pulse.includes("const word=$('#lv').hidden?null:$('#cb');if(word)")&&pulse.includes("word.classList.add('beat-word-hit')")&&pulse.includes("e.classList.add('hit')")],
 ['palavra e moldura usam o mesmo tempo de 440 ms',pulse.includes('setTimeout(()=>e.classList.remove(\\'hit\\'),440)')&&pulse.includes('setTimeout(()=>word.classList.remove(\\'beat-word-hit\\'),440)')],
 ['efeito do texto é dourado, difuso e sem deslocamento',h.includes('#stg.stage #cb.beat-word-hit')&&h.includes('transform:none!important')&&h.includes('rimalab-word-beat-v14')],
 ['pulso visual parte do relógio de saída do áudio',h.includes('const zPerf=()=>')&&h.includes('setTimeout(()=>pulse(((bt%4)+4)%4),dl)')],
 ['troca de palavra não aciona pop fora do tempo do beat',!h.includes("$('#cs').textContent=c.sub;stamp(w);WD.nw++")],
 ['palavras curtas mantêm a fonte grande',h.includes('font-size:72px!important')&&h.includes('raw.length<=12 && e.scrollWidth<=available')],
 ['R do splash permanece branco',h.includes('.splash-mark .splash-initial{color:#fff!important')],
 ['APK atualizado para 2.9.6 / versionCode 33',g.includes('versionCode 33')&&g.includes("versionName '2.9.6'")]
];
let bad=0;for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V14');
process.exit(bad?1:0);
