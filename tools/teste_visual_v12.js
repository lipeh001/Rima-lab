#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(process.argv[2]||'.');
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const start=h.indexOf('async function cal(){'),end=h.indexOf('\nconst CH=',start),cal=start>=0&&end>start?h.slice(start,end):'';
const fit=h.includes('id="rima-word-fit-script-v12"')?h.slice(h.indexOf('id="rima-word-fit-script-v12"')):'';
const keyStart=h.indexOf('const rimaKeyV12=');
const keyEnd=h.indexOf('const rimasDe=',keyStart);
const keyContext={norm:s=>(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim()};
if(keyStart>=0&&keyEnd>keyStart){try{vm.runInNewContext(h.slice(keyStart,keyEnd)+';this.key=rimaKeyV12;',keyContext)}catch(e){keyContext.key=null}}
const wStart=h.indexOf('function wWord()');
const wChunk=wStart>=0?h.slice(wStart,wStart+600):'';
const tests=[
 ['motor de rima usa a vogal tônica, não só o sufixo escrito',h.includes('const rimaKeyV12=')&&h.includes('rimaKeyV12(x)===key')&&typeof keyContext.key==='function'],
 ['DENÚNCIA não é confundida com a família -ia',keyContext.key&&keyContext.key('DENÚNCIA')==='UNCIA'&&keyContext.key('MANIA')==='IA'],
 ['MÉRITO não é confundido com a família -ito',keyContext.key&&keyContext.key('MÉRITO')==='ERITO'&&keyContext.key('GRITO')==='ITO'],
 ['palavras sem acento usam a sílaba tônica correta',keyContext.key&&keyContext.key('TERREMOTO')==='OTO'&&keyContext.key('RIVAL')==='AL'&&keyContext.key('INTELIGÊNCIA-ARTIFICIAL')==='AL'],
 ['DENÚNCIA recebe renúncia/pronúncia/anúncia',h.includes("'DENÚNCIA':['renúncia','pronúncia','anúncia']")&&h.includes("'DENUNCIA':['renúncia','pronúncia','anúncia']")],
 ['MÉRITO recebe pretérito/emérito/demérito',h.includes("'MÉRITO':['pretérito','emérito','demérito']")&&h.includes("'MERITO':['pretérito','emérito','demérito']")],
 ['lista secundária de POSTE não contém teste/veste',h.includes("'POSTE':['goste','encoste','desgoste','aposte']")&&!h.includes("'POSTE':['teste','veste','agreste','nordeste']")],
 ['palavra não recebe mais animação de entrada',wChunk&&!wChunk.includes('stamp(w)')],
 ['ajuste responsivo mede largura real e define font-size importante',fit.includes('e.scrollWidth')&&fit.includes("'important'")&&fit.includes('ResizeObserver')],
 ['não usa scaleX para esmagar a palavra',!fit.includes('scaleX(')],
 ['palco, palavras e sugestões estão em dourado',h.includes('#edc34d!important')&&h.includes('#stg.stage #cb')&&h.includes('.rm span')],
 ['pulso dourado é difuso e não desloca o palco',h.includes('rimalab-gold-pulse-v12')&&h.includes('#bt .stage.hit::after')&&h.includes('transform:none!important')],
 ['splash usa R escuro em alto contraste',h.includes('.splash-mark .splash-initial')&&h.includes('font-size:62px!important')&&h.includes('color:#17140d!important')],
 ['calibrador informa que não mede atraso físico Bluetooth',cal.includes('não mede o atraso acústico adicional da caixa Bluetooth')&&cal.includes('microfone/loopback')],
 ['0 ms não é apresentado como ausência de atraso',cal.includes('0 ms não significa ausência de atraso')],
 ['sem leitura válida não apaga o ajuste existente',!cal.includes('setLat(0)')&&cal.includes('ajuste atual foi preservado')],
 ['mantém a leitura baseLatency + outputLatency e o limite de 300 ms',cal.includes('ctx.baseLatency')&&cal.includes('ctx.outputLatency')&&cal.includes('Math.min(300')],
 ['APK tem versão 2.9.4 / versionCode 31',g.includes('versionCode 31')&&g.includes("versionName '2.9.4'")]
];
let failures=0;
for(const [name,ok] of tests){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)failures++;}
console.log((tests.length-failures)+'/'+tests.length+' verificações VISUAL_V12');
process.exit(failures?1:0);
