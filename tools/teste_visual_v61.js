#!/usr/bin/env node
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const root=path.resolve(process.argv[2]),hp=path.join(root,'app/src/main/assets/rima-lab.html');
const gp=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
if(!fs.existsSync(hp)||!gp)throw new Error('V61: HTML/Gradle ausentes');
const html=fs.readFileSync(hp,'utf8'),g=fs.readFileSync(gp,'utf8'),pass=[],fail=[],errors=[];
const check=(n,ok,d='')=>(ok?pass:fail).push({n,d});
check('versão 3.3.9/code81',/versionCode\s*(?:=\s*)?81/.test(g)&&/versionName\s*(?:=\s*)?["']3\.3\.9["']/.test(g));
check('V40 legacy renderer yields to V43',html.includes("function scheduleRender(){if(typeof window.rimaV43ShowFavorites==='function')return;"));
check('V42 delayed rerender yields to V43',html.includes("if(typeof window.rimaV43ShowFavorites!=='function'){renderAll();setTimeout(renderAll,60)}"));
check('V43 preserves Favorites DOM on player updates',html.includes('function syncToolbarOnly()')&&html.includes('oldPk.apply(this,arguments);syncToolbarOnly()')&&html.includes('oldBar.apply(this,arguments);syncToolbarOnly()'));
check('both populated and empty Favorites lists share the catalog bsl container',html.split('class="bsl rima-v43-favlist"').length===3);
check('Favorites rows reuse catalog bi and mc components',html.includes('class="bi rima-v43-fav-row"')&&html.includes('class="mc rima-v43-fav-play'));
check('Favorites selected state matches regular .mc state',html.includes('background:var(--ac)!important;color:var(--on)!important')&&html.includes('box-shadow:3px 3px 0 var(--ink)!important'));
check('landscape has fixed three-row selector layout',html.includes('grid-template-rows:40px minmax(0,1fr) 40px!important'));
check('landscape beats get a fixed-height horizontal scrolling strip',html.includes('height:112px!important')&&html.includes('flex-shrink:0!important')&&html.includes('overflow-x:auto!important;overflow-y:hidden!important')&&html.includes('flex:0 0 clamp(190px,25vw,280px)!important'));
check('all inline scripts parse',(()=>{try{for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi))new Function(m[1]);return true}catch(e){return false}})());

const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()}});window.RimaNative={baixar:()=>{},apagar:()=>{},lista:()=>"[]",mediaState:()=>{}}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>{const s=document.querySelector('#rima-splash');return !s||s.classList.contains('done')},{timeout:20000});
  const tap=async sel=>{const el=page.locator(sel).first();await el.waitFor({state:'visible',timeout:12000});await el.scrollIntoViewIfNeeded();await el.click({timeout:12000});await page.waitForTimeout(120)};
  await page.waitForSelector('#md .mc',{timeout:15000});
  await tap('#md .mc');await tap('#train-step-1 .go');
  await page.waitForFunction(()=>!document.querySelector('#train-step-2').hidden,{timeout:10000});
  await page.evaluate(async()=>{if(window.rimaCatalogReady&&typeof window.rimaCatalogReady.then==='function')await window.rimaCatalogReady; if(typeof zBuild==='function'){zBuild('Boom bap');zBuild('Trap');zBuild('Drill')}});
  await page.waitForFunction(()=>typeof ZLIB!=='undefined'&&Array.isArray(ZLIB['Boom bap']?.[1])&&ZLIB['Boom bap'][1].length>3&&!!document.querySelector('#bp .bsl .bi .mc'),{timeout:20000});
  const favoriteData=await page.evaluate(()=>{
   const c=ZLIB['Boom bap'][1],idx=Math.min(2,c.length-1),key='jm-'+String(c[idx][4]);
   localStorage.setItem('rimalab_favorites_v29',JSON.stringify([key,'jm-'+String(c[Math.min(3,c.length-1)][4])]));
   return {key,defaultKey:ZS.key||'',title:c[idx][1]};
  });
  await tap('#bp .rima-v43-toggle');
  await page.waitForFunction(()=>!!document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play'),{timeout:10000});
  const first=page.locator('#bp>.rima-v43-favlist .rima-v43-fav-play').first();
  const firstKey=await first.getAttribute('data-v43-play');
  const before=await page.evaluate(()=>{window.__v61FavoriteNode=document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play');window.__v61ZlpCalls=0;const old=window.zLP;window.zLP=function(){window.__v61ZlpCalls++;return old.apply(this,arguments)};return {key:window.__v61FavoriteNode?.getAttribute('data-v43-play'),listCount:document.querySelectorAll('#bp>.rima-v43-favlist').length,toolbarHearts:document.querySelectorAll('#bp .rima-v43-toggle .rima-v60-heart-glyph').length,toolbarButtons:document.querySelectorAll('#bp>.rima-v43-tools>button').length}});
  await first.click({timeout:10000});
  await page.waitForFunction(k=>ZS.key===k,firstKey,{timeout:7000});
  await page.waitForTimeout(700);
  const after=await page.evaluate(()=>{const n=window.__v61FavoriteNode;const b=document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play');return {key:ZS.key,nodeStillConnected:!!(n&&n.isConnected),sameNode:n===b,selected:!!b&&b.classList.contains('is-selected'),pressed:b?.getAttribute('aria-pressed'),lists:document.querySelectorAll('#bp>.rima-v43-favlist').length,catalogHidden:document.querySelector('#bp>.bsl:not(.rima-v43-favlist)')?.hidden,toolbarHearts:document.querySelectorAll('#bp .rima-v43-toggle .rima-v60-heart-glyph').length,toolbarButtons:document.querySelectorAll('#bp>.rima-v43-tools>button').length,zlpCalls:window.__v61ZlpCalls}});
  check('first tap on Favorites starts the intended beat once',after.key===firstKey&&after.zlpCalls===1,JSON.stringify({firstKey,after}));
  check('first favorite card is not rebuilt or visually deselected',after.nodeStillConnected&&after.sameNode&&after.selected&&after.pressed==='true',JSON.stringify(after));
  check('Favorites view and hidden category remain stable after player update',after.lists===1&&after.catalogHidden===true,JSON.stringify(after));
  check('toolbar renders exactly one heart icon',before.toolbarHearts===1&&after.toolbarHearts===1&&before.toolbarButtons===1&&after.toolbarButtons===1,JSON.stringify({before,after}));
  const favList=await page.evaluate(()=>{const e=document.querySelector('#bp>.rima-v43-favlist');const r=e.getBoundingClientRect();return{isBsl:e.classList.contains('bsl'),height:r.height,maxHeight:getComputedStyle(e).maxHeight,overflowY:getComputedStyle(e).overflowY}});
  check('stage 2 Favorites uses the same bounded scroll list as categories',favList.isBsl&&favList.height>40&&favList.overflowY==='auto',JSON.stringify(favList));
  await tap('#bp .rima-v50-category-row .tag.chip');
  await tap('#bp .rima-v43-toggle');
  await page.waitForFunction(()=>!!document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play'),{timeout:8000});
  const second=page.locator('#bp>.rima-v43-favlist .rima-v43-fav-play').nth(1);
  const secondKey=await second.getAttribute('data-v43-play');
  await second.click({timeout:10000});await page.waitForFunction(k=>ZS.key===k,secondKey,{timeout:7000});await page.waitForTimeout(500);
  check('returning to Favorites keeps the second selection stable',await page.evaluate(k=>ZS.key===k&&document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play[aria-pressed="true"]')?.getAttribute('data-v43-play')===k,secondKey));

  // Start the live stage and measure the actual landscape selector geometry.
  await tap('#train-step-2 .training-footer .go');
  await page.waitForFunction(()=>!document.querySelector('#lv').hidden,{timeout:12000});
  await page.setViewportSize({width:1536,height:691});
  await page.evaluate(()=>{window.dispatchEvent(new Event('orientationchange'));window.dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(650);
  const layout=await page.evaluate(()=>{
   const rect=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return{x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),display:c.display,overflowX:c.overflowX,overflowY:c.overflowY,grid:c.gridTemplateRows}};
   return{bodyClass:document.body.className,lv:rect('#lv'),stage:rect('#stg'),card:rect('#lv>.card:not(.stage)'),bq:rect('#bq'),list:rect('#bq>.bsl:not([hidden])'),rows:document.querySelectorAll('#bq>.bsl:not([hidden])>.bi').length,nav:getComputedStyle(document.querySelector('nav')).display};
  });
  const l=layout.list;
  check('landscape selector has a real visible beat list',!!l&&l.h>=90&&l.w>160&&l.display!=='none'&&l.overflowX==='auto',JSON.stringify(layout));
  check('landscape beat cards are horizontally scrollable',await page.evaluate(()=>{const e=document.querySelector('#bq>.bsl:not([hidden])');return !!e&&e.scrollWidth>e.clientWidth&&getComputedStyle(e).touchAction.includes('pan-x')}),JSON.stringify(layout));
  check('selector list stays inside the live card',!!layout.card&&!!layout.bq&&!!layout.list&&layout.list.y>=layout.bq.y&&layout.list.y+layout.list.h<=layout.card.y+layout.card.h+2,JSON.stringify(layout));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.n+(x.d?' — '+x.d:''));for(const x of fail)console.log('FAIL '+x.n+(x.d?' — '+x.d:''));console.log('V61_RESULT '+pass.length+' passed; '+fail.length+' failed');
 if(fail.length||errors.length){for(const e of errors)console.log('JS_ERROR '+e);process.exit(1)}
})().catch(e=>{console.error(e);process.exit(1)});
