const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const m=h.match(/function pulse\(q\)\{[\s\S]*?\n\}/);
const checks=[
 ['camada própria da moldura',h.includes('rima-beat-frame')],
 ['moldura absoluta fora do fluxo do layout',h.includes('position:absolute!important;')&&h.includes('inset:4px!important;')],
 ['pulso de 2,2% com retorno ao tamanho base',h.includes('0.022*Math.max(0,strength)')&&h.includes("scale(1)")],
 ['pulso chamado pelo relógio do beat',!!m&&m[0].includes('rimaPulseStageFrame();')],
 ['pseudomolduras antigas desativadas',h.includes('#lv:not([hidden]) #stg.stage::after')&&h.includes('content:none!important')],
 ['palavra não recebe transform nem animação',h.includes('#lv:not([hidden]) #stg.stage #cb *')&&h.includes('transform:none!important')],
 ['versão 3.0.5 / code 47',g.includes('versionCode 47')&&g.includes("versionName '3.0.5'")]
];
let fail=0;
for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)fail++}
if(fail)process.exit(1);
console.log('V27_TESTS_OK');