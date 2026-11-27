#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gradlePath=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
const gradle=fs.readFileSync(gradlePath,'utf8');
const pass=[],fail=[],errors=[];
const ok=(name,c,detail='')=>(c?pass:fail).push({name,detail});
const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()}});window.RimaNative={baixar:()=>{},apagar:()=>{},lista:()=>"[]"}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>{const e=document.querySelector('#rima-splash');return !e||e.classList.contains('done')},{timeout:15000});
  await page.waitForSelector('#train-step-1',{timeout:15000});

  async function testScroll(label,selector,width,height){
   await page.setViewportSize({width,height});
   await page.evaluate(()=>{dispatchEvent(new Event('orientationchange'));dispatchEvent(new Event('resize'))});
   await page.waitForTimeout(350);
   await page.evaluate(sel=>{
    const target=document.querySelector(sel);if(!target)throw Error('Missing scroll target '+sel);
    document.getElementById('rima-scroll-probe')?.remove();
    const probe=document.createElement('div');probe.id='rima-scroll-probe';
    probe.style.cssText='display:block!important;position:relative!important;width:100%!important;height:820px!important;min-height:820px!important;pointer-events:none!important';
    target.appendChild(probe);
    window.scrollTo(0,0);const root=document.scrollingElement||document.documentElement;root.scrollTop=0;
   },selector);
   const before=await page.evaluate(sel=>{
    const target=document.querySelector(sel),main=document.querySelector('main'),root=document.scrollingElement||document.documentElement;
    return {target:sel,active:!!target&&!target.hidden,rootHeight:root.scrollHeight,viewport:innerHeight,
     htmlOverflow:getComputedStyle(document.documentElement).overflowY,bodyOverflow:getComputedStyle(document.body).overflowY,
     mainPosition:getComputedStyle(main).position,mainOverflow:getComputedStyle(main).overflowY,
     touch:getComputedStyle(main).touchAction,probe:!!document.getElementById('rima-scroll-probe')};
   },selector);
   await page.mouse.move(width*.75,height*.62);
   await page.mouse.wheel(0,620);
   await page.waitForTimeout(180);
   const after=await page.evaluate(()=>({root:(document.scrollingElement||document.documentElement).scrollTop,window:window.scrollY,body:document.body.scrollTop}));
   ok(label+' has a real document scroll range',before.active&&before.probe&&before.rootHeight>before.viewport+300,JSON.stringify(before));
   ok(label+' is not trapped in a fixed/hidden main',before.mainPosition!=='fixed'&&before.mainOverflow!=='hidden'&&before.htmlOverflow!=='hidden'&&before.touch.includes('pan-y'),JSON.stringify(before));
   ok(label+' responds to vertical scroll input',Math.max(after.root,after.window,after.body)>0,JSON.stringify({before,after}));
   await page.evaluate(()=>document.getElementById('rima-scroll-probe')?.remove());
   await page.evaluate(()=>window.scrollTo(0,0));
  }

  for(const [label,width,height] of [['portrait',393,852],['landscape',852,393]]){
   await testScroll('Treino · etapa 1 · '+label,'#train-step-1',width,height);
   if(!await page.locator('#train-step-2').isVisible())await page.locator('#train-step-1 .go').click({timeout:8000});
   await page.waitForFunction(()=>!document.querySelector('#train-step-2').hidden,{timeout:8000});
   await testScroll('Treino · etapa 2 · '+label,'#train-step-2',width,height);
   await page.locator('#train-step-2 .bk').click({timeout:8000});
   await page.waitForFunction(()=>!document.querySelector('#train-step-1').hidden,{timeout:8000});
  }

  await page.evaluate(()=>go(2));
  await page.waitForTimeout(180);
  await testScroll('Batalha · portrait','#bt',393,852);
  await testScroll('Batalha · landscape','#bt',852,393);
  await page.evaluate(()=>go(1));
  await page.waitForTimeout(180);
  await testScroll('Aulas · portrait','#al',393,852);
  await testScroll('Aulas · landscape','#al',852,393);

  ok('version 3.3.2 / code 74',/versionCode\s*=\s*74|versionCode\s+74/.test(gradle)&&/versionName\s*=\s*['"]3\.3\.2['"]|versionName\s+['"]3\.3\.2['"]/.test(gradle));
  ok('generic .pl main lock removed',!html.includes('body.pl:not(.pv) main,body.pl.sy:not(.pv) main{')&&html.includes('body.rima-live-landscape main{'));
  ok('V52 no longer writes inline scroll geometry to main',!html.includes("main.style.setProperty('position'" )&&!html.includes("main.style.setProperty('overflow-y'"));
  ok('no uncaught JavaScript errors',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' :: '+x.detail:''));
 for(const x of fail)console.log('FAIL '+x.name+(x.detail?' :: '+x.detail:''));
 console.log(pass.length+' passed / '+fail.length+' failed');
 if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
