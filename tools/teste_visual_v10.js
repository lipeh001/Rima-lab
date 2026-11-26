#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const assets=path.join(root,'app/src/main/assets');
const h=fs.readFileSync(path.join(assets,'rima-lab.html'),'utf8');
const gradle=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const seedScript=fs.readFileSync(path.resolve(__dirname,'fetch_catalog_seed.js'),'utf8');
const calStart=h.indexOf('async function cal(){');
const calEnd=h.indexOf('\nconst CH=',calStart);
const cal=calStart>=0&&calEnd>calStart?h.slice(calStart,calEnd):'';
const cssStart=h.indexOf('<style id="rima-visual-v10">');
const cssEnd=h.indexOf('</style>',cssStart);
const css=cssStart>=0&&cssEnd>cssStart?h.slice(cssStart,cssEnd):'';
const checks=[
 ['tema usa dourado do símbolo como cor principal',css.includes('--ac:#edc34d')&&css.includes('--hl:#f4cf62')],
 ['roxo está presente como cor de apoio',css.includes('--ac2:#a58ae8')&&css.includes('--g2:#a58ae8')],
 ['fundo permanece escuro e os verdes deixam de dominar o tema',css.includes('--bg:#0b0b10')&&css.includes('--ok:#72d7b5')],
 ['em paisagem a navegação inferior fica escondida',/@media \(orientation:landscape\) and \(max-height:850px\)\s*\{[\s\S]*?nav\{display:none!important/.test(css)],
 ['em paisagem o player ocupa o rodapé sem ficar atrás da navegação',css.includes('#pbar{display:flex!important;left:8px!important;right:8px!important;bottom:calc(7px')],
 ['em retrato a navegação continua visível e o player mantém sua posição',/@media \(orientation:portrait\)\s*\{[\s\S]*?nav\{display:grid!important/.test(css)&&css.includes('#pbar{bottom:calc(72px')],
 ['texto do seletor é curto e não fala de licença',h.includes('Escolha um beat para ouvir e treinar.')&&!h.includes('Quando a licença permitir, o beat será salvo automaticamente')],
 ['calibrador automático não pede microfone',cal.includes('ctx.baseLatency')&&!cal.includes('getUserMedia')],
 ['calibrador reúne várias leituras do aparelho',cal.includes('for(let i=0;i<9;i++)')&&cal.includes('values.sort((a,b)=>a-b)')],
 ['calibrador estabiliza resultado em precisão de 1ms',cal.includes('Math.round(measured)')&&cal.includes('values[Math.floor(values.length/2)]')],
 ['texto do calibrador deixa claro que não precisa aumentar volume',h.includes('Não precisa de microfone nem de aumentar o volume.')],
 ['catálogo exige classificação explícita de instrumental no Jamendo',seedScript.includes("if (vocal !== 'instrumental') return -1;")&&h.includes("if(vi!=='instrumental')return 9;")],
 ['catálogo rejeita títulos de música/som cantado sem marcação de beat',seedScript.includes('music|burger|song|anthem|lyrics|vocal')],
 ['APK terá versão 2.9.2 e atualizará a instalação anterior',gradle.includes('versionCode 29')&&gradle.includes("versionName '2.9.2'")]
];
let bad=0;
for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log((checks.length-bad)+'/'+checks.length+' verificações VISUAL_V10');
process.exit(bad?1:0);
