#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]),hp=path.join(root,'app/src/main/assets/rima-lab.html');
const gp=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
if(!fs.existsSync(hp)||!gp)throw new Error('V56: HTML/Gradle ausentes');
const h=fs.readFileSync(hp,'utf8'),g=fs.readFileSync(gp,'utf8'),pass=[],fail=[];
const check=(name,ok,detail='')=>(ok?pass:fail).push({name,detail});
check('base V54 preservada',h.includes('rimalab-unified-catalog-favorites-v54'));
check('versão 3.3.4/code76',/versionCode\s*(?:=\s*)?76/.test(g)&&/versionName\s*(?:=\s*)?["']3\.3\.4["']/.test(g));
check('títulos favoritos normalizam espaços',h.includes("normalize('NFC').replace(/\\s+/gu,' ').trim()"));
check('runtime SVG do coração existe',h.includes('rimalab-centered-heart-runtime-v56')&&h.includes("setAttribute('viewBox','0 0 24 24')"));
check('SVG sincroniza estado ativo/inativo',h.includes("existing.setAttribute('data-filled',on?'true':'false')"));
check('runtime observa classes, aria-pressed e texto',h.includes("attributeFilter:['class','aria-pressed']")&&h.includes('characterData:true'));
check('passo 2 recebe recuo dos dois lados',h.includes('padding:0 6px!important')&&h.includes('padding:6px 9px 8px!important'));
check('seletor vertical reserva área útil',h.includes('min-height:min(20vh,175px)!important')&&h.includes('max-height:min(26vh,220px)!important'));
check('lista horizontal ganha faixa própria',h.includes('grid-template-columns:minmax(0,1fr) 88px!important')&&h.includes('grid-template-rows:30px 12px minmax(0,1fr)!important'));
check('dica horizontal fica dentro do palco',h.includes('margin:auto auto 1px!important')&&h.includes('overflow:hidden!important'));
const runtime=h.match(/<script\b[^>]*id=["']rimalab-centered-heart-runtime-v56["'][^>]*>([\s\S]*?)<\/script>/);
check('runtime vetorial presente no HTML final',!!runtime);
let syntax=false,syntaxError='';
try{if(runtime)new Function(runtime[1]);syntax=true}catch(e){syntaxError=String(e)}
check('runtime do coração tem sintaxe JavaScript válida',syntax,syntaxError);
for(const x of pass)console.log('PASS '+x.name+(x.detail?' — '+x.detail:''));
for(const x of fail)console.log('FAIL '+x.name+(x.detail?' — '+x.detail:''));
console.log('V56_RESULT '+pass.length+' passed; '+fail.length+' failed');
if(fail.length)process.exit(1);
