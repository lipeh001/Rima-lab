#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gradlePath=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
const gradle=fs.readFileSync(gradlePath,'utf8');
const pass=[],fail=[],errors=[];const ok=(n,c,d='')=>(c?pass:fail).push({name:n,detail:d});
const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()}});window.RimaNative={baixar:()=>{},apagar:()=>{},lista:()=>"[]"}})()</script>';
(async()=>{const browser=await chromium.launch({headless:true,args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});page.on('pageerror',e=>errors.push(String(e)));
 await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:30000});
 await page.waitForFunction(()=>{const e=document.querySelector('#rima-splash');return !e||e.classList.contains('done')},{timeout:15000});
 await page.waitForSelector('#train-step-1',{timeout:15000});
 await page.setViewportSize({width:852,height:393});await page.evaluate(()=>{dispatchEvent(new Event('orientationchange'));dispatchEvent(new Event('resize'))});await page.waitForTimeout(450);
 const nav=await page.evaluate(()=>{const n=document.querySelector('nav'),r=n.getBoundingClientRect();return{display:getComputedStyle(n).display,visibility:getComputedStyle(n).visibility,pointer:getComputedStyle(n).pointerEvents,rect:{top:r.top,bottom:r.bottom,width:r.width,height:r.height},labels:[...n.querySelectorAll('button')].map(b=>b.textContent.trim()),player:getComputedStyle(document.querySelector('#pbar')).display,mainPosition:getComputedStyle(document.querySelector('main')).position,mainOverflow:getComputedStyle(document.querySelector('main')).overflow,scrollHeight:document.documentElement.scrollHeight,clientHeight:innerHeight}});
 ok('landscape shows all three navigation tabs',nav.display==='grid'&&nav.visibility==='visible'&&nav.pointer==='auto'&&nav.labels.some(x=>x.includes('Treino'))&&nav.labels.some(x=>x.includes('Batalha'))&&nav.labels.some(x=>x.includes('Aulas')),JSON.stringify(nav));
 ok('setup does not show the audio player over navigation',nav.player==='none');
 const mode=page.locator('#md .mc').first();await mode.waitFor({state:'visible',timeout:8000});const box=await mode.boundingBox();if(box)await page.mouse.click(box.x+box.width/2,box.y+box.height/2);
 ok('mode cards accept taps in landscape',await mode.evaluate(e=>e.classList.contains('on')));
 await page.locator('nav button[data-i="1"]').click({timeout:8000});await page.waitForTimeout(120);
 ok('Aulas navigation button works in landscape',await page.locator('.tab').nth(1).evaluate(e=>!e.hidden));
 await page.locator('nav button[data-i="0"]').click({timeout:8000});await page.waitForTimeout(120);
 ok('Treino navigation button returns to setup in landscape',await page.locator('#ao').evaluate(e=>!e.hidden));
 await page.locator('#train-step-1 .go').click({timeout:8000});await page.waitForTimeout(180);
 const scroll=await page.evaluate(()=>({mainOverflow:getComputedStyle(document.querySelector('main')).overflowY,bodyOverflow:getComputedStyle(document.body).overflowY,mainPosition:getComputedStyle(document.querySelector('main')).position,mainScroll:document.querySelector('main').scrollHeight,mainClient:document.querySelector('main').clientHeight,navBottom:document.querySelector('nav').getBoundingClientRect().bottom}));
 ok('landscape setup remains scrollable after advancing to step 2',scroll.mainOverflow!=='hidden'&&scroll.bodyOverflow!=='hidden'&&scroll.mainPosition!=='fixed'&&scroll.mainScroll>=scroll.mainClient,JSON.stringify(scroll));
 await page.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));await page.waitForTimeout(100);
 const afterScroll=await page.evaluate(()=>window.scrollY||(document.scrollingElement&&document.scrollingElement.scrollTop)||0);
 ok('vertical drag/scroll moves the setup screen in landscape',afterScroll>0,String(afterScroll));
 ok('version 3.3.1 / code 73',/versionCode\s*=\s*73|versionCode\s+73/.test(gradle)&&/versionName\s*=\s*['"]3\.3\.1['"]|versionName\s+['"]3\.3\.1['"]/.test(gradle));
 ok('no uncaught JavaScript errors',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' :: '+x.detail:''));for(const x of fail)console.log('FAIL '+x.name+(x.detail?' :: '+x.detail:''));console.log(pass.length+' passed / '+fail.length+' failed');if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
