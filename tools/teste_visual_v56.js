#!/usr/bin/env node
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const root=path.resolve(process.argv[2]),hp=path.join(root,'app/src/main/assets/rima-lab.html');
const gp=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
if(!fs.existsSync(hp)||!gp)throw new Error('V56: HTML/Gradle ausentes');
const h=fs.readFileSync(hp,'utf8'),g=fs.readFileSync(gp,'utf8'),pass=[],fail=[],errors=[];
const check=(name,ok,detail='')=>(ok?pass:fail).push({name,detail});
check('base V54 preservada',h.includes('rimalab-unified-catalog-favorites-v54'));
check('versão 3.3.4/code76',/versionCode\s*(?:=\s*)?76/.test(g)&&/versionName\s*(?:=\s*)?["']3\.3\.4["']/.test(g));
check('títulos favoritos normalizam espaços',h.includes("normalize('NFC').replace(/\\s+/gu,' ').trim()"));
check('runtime SVG de coração',h.includes('rimalab-centered-heart-runtime-v56')&&h.includes("setAttribute('viewBox','0 0 24 24')"));
check('passo 2 tem recuo dos dois lados',h.includes('padding:0 6px!important')&&h.includes('padding:6px 9px 8px!important'));
check('seletor vertical reserva área útil',h.includes('min-height:min(20vh,175px)!important')&&h.includes('max-height:min(26vh,220px)!important'));
check('lista horizontal tem faixa própria',h.includes('grid-template-columns:minmax(0,1fr) 88px!important')&&h.includes('grid-template-rows:30px 12px minmax(0,1fr)!important'));
check('dica horizontal fica dentro do palco',h.includes('margin:auto auto 1px!important')&&h.includes('overflow:hidden!important'));
const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(String(k)),clear:()=>m.clear()}});window.RimaNative={baixar:()=>{},apagar:()=>{},lista:()=>"[]",mediaState:()=>{},chave:()=>"",buscar:()=>{}}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:873},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+h,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>typeof window.trainNext==='function'&&document.querySelector('#bp'),{timeout:15000});
  await page.evaluate(()=>{document.querySelector('#rima-splash')?.classList.add('done');window.trainNext();window.pk?.()});
  await page.waitForFunction(()=>document.querySelector('#train-step-2 #bp>.bsl .bi'),{timeout:12000});
  await page.waitForTimeout(150);
  const step=await page.evaluate(()=>{const l=document.querySelector('#train-step-2 #bp>.bsl'),r=l?.querySelector('.bi');if(!l||!r)return null;const a=l.getBoundingClientRect(),b=r.getBoundingClientRect();return{left:b.left-a.left,right:a.right-b.right,client:l.clientWidth,scroll:l.scrollWidth}});
  check('passo 2 sem corte lateral',!!step&&step.left>=5&&step.right>=1&&step.scroll<=step.client+1,JSON.stringify(step));
  const fav=await page.evaluate(()=>{const z=typeof ZLIB!=='undefined'?ZLIB:window.ZLIB,grp=z&&(z['Boom bap']||z['Boom Bap']),item=grp&&grp[1]&&grp[1][0];if(!item||item[4]==null||typeof window.rimaV43ShowFavorites!=='function')return{ok:false};item[1]='Beat   Title    With     Irregular   Spaces';const k='jm-'+String(item[4]);localStorage.setItem('rimalab_favorites_v29',JSON.stringify([k]));window.rimaV43ShowFavorites(true);return{ok:true}});
  if(fav.ok){await page.waitForFunction(()=>document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play'),{timeout:7000});await page.waitForTimeout(120);const x=await page.evaluate(()=>{const b=document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play b'),s=document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-heart svg.rima-heart-icon'),r=s?.getBoundingClientRect();return{title:b?.textContent||'',svg:!!s,size:r?[r.width,r.height]:null}});check('favoritos remove espaços repetidos',x.title==='Beat Title With Irregular Spaces',JSON.stringify(x));check('coração SVG quadrado',x.svg&&x.size&&Math.abs(x.size[0]-x.size[1])<=1&&x.size[0]>=18,JSON.stringify(x))}else check('catálogo disponível para teste de Favoritos',false,'não localizou a primeira faixa Boom bap');
  await page.evaluate(()=>{window.rimaV43ShowFavorites?.(false);window.pk?.();window.zLP?.(0,0,'Boom bap');window.pk?.();const a=document.querySelector('#train-step-1');if(a)a.hidden=true;const b=document.querySelector('#train-step-2');if(b)b.hidden=true;const lv=document.querySelector('#lv');if(lv)lv.hidden=false;document.body.classList.add('pl','treino');document.body.classList.remove('pv','rima-live-landscape');document.documentElement.classList.remove('rima-live-landscape');const n=document.querySelector('#cn');if(n)n.textContent='Virada detectada. Entrando um pouco antes dela.'});
  await page.waitForTimeout(250);
  const v=await page.evaluate(()=>{const s=document.querySelector('#stg'),t=s?.querySelector('.v3bar'),l=document.querySelector('#bq>.bsl:not([hidden])'),n=document.querySelector('#cn');if(!s||!t||!l)return null;const a=s.getBoundingClientRect(),b=t.getBoundingClientRect(),c=n?.getBoundingClientRect(),d=l.getBoundingClientRect();return{height:d.height,stage:[a.left,a.top,a.right,a.bottom],tip:[b.left,b.top,b.right,b.bottom],messageBottom:c?.bottom}});
  check('seletor vertical tem área útil',!!v&&v.height>=170,JSON.stringify(v));
  check('dica vertical no palco com respiro',!!v&&v.tip[0]>=v.stage[0]&&v.tip[2]<=v.stage[2]&&v.tip[3]<=v.stage[3]&&v.tip[1]-v.messageBottom>=8,JSON.stringify(v));
  await page.setViewportSize({width:873,height:393});
  await page.evaluate(()=>{document.body.classList.add('pl','treino','rima-live-landscape');document.body.classList.remove('pv');document.documentElement.classList.add('rima-live-landscape');const a=document.querySelector('#ck');if(a)a.textContent='Palavra de ação';const b=document.querySelector('#cb');if(b)b.textContent='ACABAR'});
  await page.waitForTimeout(250);
  const l=await page.evaluate(()=>{const s=document.querySelector('#stg'),t=s?.querySelector('.v3bar'),b=document.querySelector('#bq>.bsl:not([hidden])');if(!s||!t||!b)return null;const a=s.getBoundingClientRect(),c=t.getBoundingClientRect(),d=b.getBoundingClientRect();return{height:d.height,stage:[a.left,a.top,a.right,a.bottom],tip:[c.left,c.top,c.right,c.bottom]}});
  check('lista horizontal visível',!!l&&l.height>=60,JSON.stringify(l));
  check('dica horizontal dentro do palco',!!l&&l.tip[0]>=l.stage[0]&&l.tip[2]<=l.stage[2]&&l.tip[1]>=l.stage[1]&&l.tip[3]<=l.stage[3],JSON.stringify(l));
  check('sem exceções JavaScript',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' — '+x.detail:''));
 for(const x of fail)console.log('FAIL '+x.name+(x.detail?' — '+x.detail:''));
 console.log('V56_RESULT '+pass.length+' passed; '+fail.length+' failed');
 if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
