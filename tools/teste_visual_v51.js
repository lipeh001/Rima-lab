#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gradlePath=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
const gradle=fs.readFileSync(gradlePath,'utf8');
const pass=[],fail=[],errors=[];
const ok=(name,c,d='')=>(c?pass:fail).push({name,detail:d});
const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()}});window.RimaNative={baixar:()=>{},apagar:()=>{},lista:()=>"[]"}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>{const e=document.querySelector('#rima-splash');return !e||e.classList.contains('done')},{timeout:15000});
  await page.waitForSelector('#train-step-1',{timeout:15000});
  const setup=await page.evaluate(()=>({hidden:document.querySelector('#train-step-1').hidden,player:getComputedStyle(document.querySelector('#pbar')).display,eligible:document.body.classList.contains('rima-v51-player-eligible')}));
  ok('step 1 opens usable and player is absent in portrait',!setup.hidden&&setup.player==='none'&&!setup.eligible,JSON.stringify(setup));
  await page.setViewportSize({width:852,height:393});
  await page.evaluate(()=>{dispatchEvent(new Event('orientationchange'));dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(450);
  const wide=await page.evaluate(()=>({player:getComputedStyle(document.querySelector('#pbar')).display,position:document.querySelector('#pbar').style.position,eligible:document.body.classList.contains('rima-v51-player-eligible'),step1:!document.querySelector('#train-step-1').hidden}));
  ok('step 1 remains interactive in landscape with no player overlay',wide.player==='none'&&!wide.eligible&&wide.step1&&!wide.position,JSON.stringify(wide));
  const mode=page.locator('#md .mc').first();
  await mode.waitFor({state:'visible',timeout:8000});
  const box=await mode.boundingBox();
  if(box)await page.mouse.click(box.x+box.width/2,box.y+box.height/2);
  await page.waitForTimeout(150);
  const modeSelected=await page.locator('#md .mc').first().evaluate(e=>e.classList.contains('on')||e.getAttribute('aria-pressed')==='true');
  ok('step 1 mode choice responds to a real tap in landscape',modeSelected);
  await page.setViewportSize({width:393,height:852});
  await page.evaluate(()=>{dispatchEvent(new Event('orientationchange'));dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(220);
  const next=page.locator('#train-step-1 .go').first();await next.waitFor({state:'visible',timeout:8000});
  await next.scrollIntoViewIfNeeded();await next.click({timeout:8000});
  await page.waitForTimeout(350);
  const step2=await page.evaluate(()=>({one:document.querySelector('#train-step-1').hidden,two:!document.querySelector('#train-step-2').hidden,player:getComputedStyle(document.querySelector('#pbar')).display}));
  ok('step 1 continue button advances to step 2 without player appearing',step2.one&&step2.two&&step2.player==='none',JSON.stringify(step2));
  // Simulate a running beat before entering the live stage; the player should
  // still remain hidden until the user moves into the live stage.
  await page.evaluate(()=>document.body.classList.add('rima-player-visible'));
  await page.waitForTimeout(180);
  const setupAudio=await page.evaluate(()=>getComputedStyle(document.querySelector('#pbar')).display);
  ok('audio flag alone does not show the player during setup',setupAudio==='none',setupAudio);
  await page.evaluate(()=>{
   const lv=document.querySelector('#lv');
   if(lv){lv.hidden=false;lv.style.display='';}
   const setup=document.querySelector('#train-step-2');if(setup)setup.hidden=true;
   document.body.classList.add('pl');document.body.classList.remove('pv');
   if(window.rimaV51SyncPlayer)window.rimaV51SyncPlayer();
  });
  await page.waitForTimeout(350);
  const live=await page.evaluate(()=>({display:getComputedStyle(document.querySelector('#pbar')).display,eligible:document.body.classList.contains('rima-v51-player-eligible'),count:document.querySelectorAll('#pbar').length}));
  ok('player appears only after entering the live stage with audio active',live.display!=='none'&&live.eligible&&live.count===1,JSON.stringify(live));
  await page.evaluate(()=>{document.querySelector('#lv').hidden=true;document.body.classList.remove('pl');if(window.rimaV51SyncPlayer)window.rimaV51SyncPlayer()});
  await page.waitForTimeout(250);
  const exit=await page.evaluate(()=>({display:getComputedStyle(document.querySelector('#pbar')).display,eligible:document.body.classList.contains('rima-v51-player-eligible')}));
  ok('leaving the live stage hides the player even if audio flag remains',exit.display==='none'&&!exit.eligible,JSON.stringify(exit));
  ok('version 3.3.0 / code 72',/versionCode\s*=\s*72|versionCode\s+72/.test(gradle)&&/versionName\s*=\s*['"]3\.3\.0['"]|versionName\s+['"]3\.3\.0['"]/.test(gradle));
  ok('no uncaught JavaScript errors',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' :: '+x.detail:''));
 for(const x of fail)console.log('FAIL '+x.name+(x.detail?' :: '+x.detail:''));
 console.log(pass.length+' passed / '+fail.length+' failed');
 if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
