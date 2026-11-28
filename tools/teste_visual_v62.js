#!/usr/bin/env node
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const root=path.resolve(process.argv[2]),hp=path.join(root,'app/src/main/assets/rima-lab.html');
const gp=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
if(!fs.existsSync(hp)||!gp)throw new Error('V62: HTML/Gradle ausentes');
const html=fs.readFileSync(hp,'utf8'),g=fs.readFileSync(gp,'utf8'),pass=[],fail=[],errors=[];
const check=(n,ok,d='')=>(ok?pass:fail).push({n,d});
check('versão 3.4.0/code82',/versionCode\s*(?:=\s*)?82/.test(g)&&/versionName\s*(?:=\s*)?["']3\.4\.0["']/.test(g));
check('V54 decorator ignores Favorites rows',html.includes("row.classList.contains('rima-v43-fav-row')||row.closest('.rima-v43-favlist')"));
check('V62 player heart synchronizes from current selected key and saved Favorites',html.includes('function syncPlayerHeart()')&&html.includes("b.setAttribute('aria-pressed',String(on))"));
check('V62 category selection updates active and pressed state',html.includes('function syncCategories()')&&html.includes("chip.classList.toggle('active',on)")&&html.includes("chip.setAttribute('aria-pressed',String(on))"));
check('V62 restores saved scroll instead of resetting to top',html.includes('savedStageScroll')&&html.includes('window.rimaReturnPreviousScreenToTop=wrapped')&&html.includes('window.scrollTo(0,y)'));
check('V62 republishes the first-entry turn message',html.includes('window.wStart=wrapped')&&html.includes('Virada detectada. Entrando um pouco antes dela.'));
check('V62 increases portrait live selector viewport',html.includes('max-height:min(36vh,400px)!important')&&html.includes('min-height:min(22vh,240px)!important'));
check('V62 heart controls use a single centered pseudo glyph',html.includes('rimalab-favorites-player-scroll-stage-style-v62')&&html.includes('place-items:center!important')&&html.includes("b.textContent=''"));
check('all inline scripts parse',(()=>{try{for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi))new Function(m[1]);return true}catch(e){return false}})());

const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()}});window.RimaNative={baixar:()=>{},apagar:()=>{},lista:()=>"[]",mediaState:()=>{}}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>{const s=document.querySelector('#rima-splash');return !s||s.classList.contains('done')},{timeout:20000});
  const tap=async sel=>{const el=page.locator(sel).first();await el.waitFor({state:'visible',timeout:12000});await el.scrollIntoViewIfNeeded();await el.click({timeout:12000});await page.waitForTimeout(160)};
  await page.waitForSelector('#md .mc',{timeout:15000});
  await tap('#md .mc');await tap('#train-step-1 .go');
  await page.waitForFunction(()=>!document.querySelector('#train-step-2').hidden,{timeout:10000});
  await page.evaluate(async()=>{if(window.rimaCatalogReady&&typeof window.rimaCatalogReady.then==='function')await window.rimaCatalogReady;if(typeof zBuild==='function'){zBuild('Boom bap');zBuild('Trap');zBuild('Drill')}});
  await page.waitForFunction(()=>typeof ZLIB!=='undefined'&&Array.isArray(ZLIB['Boom bap']?.[1])&&ZLIB['Boom bap'][1].length>3&&!!document.querySelector('#bp .bsl .bi .mc'),{timeout:20000});
  const fav=await page.evaluate(()=>{
   const c=ZLIB['Boom bap'][1],a=c[Math.min(2,c.length-1)],b=c[Math.min(3,c.length-1)];
   const keys=['jm-'+String(a[4]),'jm-'+String(b[4])];
   localStorage.setItem('rimalab_favorites_v29',JSON.stringify(keys));
   return {key:keys[0],second:keys[1]};
  });
  await tap('#bp .rima-v43-toggle');
  await page.waitForFunction(()=>!!document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play'),{timeout:10000});
  await page.waitForTimeout(350);
  const heartRows=await page.evaluate(()=>Array.from(document.querySelectorAll('#bp>.rima-v43-favlist .rima-v43-fav-row')).map(row=>({
   canonical:row.querySelectorAll('button.rima-v43-fav-heart,button[data-v43-heart]').length,
   injected:row.querySelectorAll('button[data-rima-fav]').length,
   doubleLegacy:row.querySelectorAll('button.rima-v29-fav:not(.rima-v43-fav-heart)').length,
   download:row.querySelectorAll('button.rima-v47-fav-download').length,
   heartText:row.querySelector('button.rima-v43-fav-heart')?.textContent
  })));
  check('each Favorites row has one heart control and no injected duplicate',heartRows.length===2&&heartRows.every(x=>x.canonical===1&&x.injected===0&&x.doubleLegacy===0),JSON.stringify(heartRows));
  const first=page.locator('#bp>.rima-v43-favlist .rima-v43-fav-play').first();
  await first.click({timeout:10000});
  await page.waitForFunction(k=>ZS.key===k,fav.key,{timeout:7000});
  await page.waitForFunction(()=>{const b=document.querySelector('#pbar #rima-v29-player-heart');return !!b&&b.classList.contains('on')&&b.getAttribute('aria-pressed')==='true'},{timeout:7000});
  const player=await page.evaluate(()=>{const b=document.querySelector('#pbar #rima-v29-player-heart');const c=getComputedStyle(b,'::before');return{on:b.classList.contains('on'),pressed:b.getAttribute('aria-pressed'),text:b.textContent,content:c.content,rect:(()=>{const r=b.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}})()}});
  check('player heart is immediately filled when a saved favorite is selected',player.on&&player.pressed==='true'&&player.text===''&&player.content.includes('♥'),JSON.stringify(player));

  // The category chip click must switch the category and restore its selected color.
  await tap('#bp .rima-v50-category-row .tag.chip:nth-child(2)');
  await page.waitForFunction(()=>ZS.s==='Trap',{timeout:7000});
  await page.waitForFunction(()=>document.querySelector('#bp .rima-v50-category-row .tag.chip:nth-child(2)')?.classList.contains('on'),{timeout:4000});
  const category=await page.evaluate(()=>Array.from(document.querySelectorAll('#bp .rima-v50-category-row .tag.chip')).map(x=>({label:x.textContent.trim(),on:x.classList.contains('on'),active:x.classList.contains('active'),pressed:x.getAttribute('aria-pressed')})));
  check('Boom bap/Trap/Drill category button reflects the active category',category.filter(x=>x.on).length===1&&category[1].on&&category[1].pressed==='true',JSON.stringify(category));

  // Open Favorites again and confirm the second favorite can be played with player state.
  await tap('#bp .rima-v43-toggle');
  await page.waitForFunction(()=>!!document.querySelector('#bp>.rima-v43-favlist .rima-v43-fav-play'),{timeout:8000});
  const second=page.locator('#bp>.rima-v43-favlist .rima-v43-fav-play').nth(1);
  await second.click({timeout:10000});
  await page.waitForFunction(k=>ZS.key===k,fav.second,{timeout:7000});
  await page.waitForFunction(()=>document.querySelector('#pbar #rima-v29-player-heart')?.getAttribute('aria-pressed')==='true',{timeout:7000});

  // Check the first-entry message even when wStart is invoked on the initial stage pass.
  await page.evaluate(()=>{if(typeof window.wStart==='function')window.wStart()});
  const message=await page.locator('#cs').textContent().catch(()=> '');
  check('first stage entry publishes the turn-detected message',message.includes('Virada detectada')||message.includes('Beat sem introdução'),message);

  // Enter stage and verify that the portrait selector viewport can show complete rows.
  await page.evaluate(()=>window.scrollTo(0,180));
  await page.waitForTimeout(100);
  const expectedScroll=await page.evaluate(()=>window.scrollY);
  await page.evaluate(()=>{if(typeof window.lvStart==='function')window.lvStart()});
  await page.waitForFunction(()=>!document.querySelector('#lv').hidden,{timeout:12000});
  await page.waitForTimeout(300);
  const portrait=await page.evaluate(()=>{
   const e=document.querySelector('#lv:not([hidden]) #bq>.bsl:not([hidden]),#lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden])');
   if(!e)return null;const r=e.getBoundingClientRect(),s=getComputedStyle(e);
   return{height:r.height,minHeight:s.minHeight,maxHeight:s.maxHeight,overflowY:s.overflowY,rows:e.querySelectorAll(':scope > .bi,:scope > .rima-v43-fav-row').length};
  });
  check('portrait stage selector has enough scroll viewport for complete beat cards',!!portrait&&portrait.height>=220&&portrait.overflowY==='auto',JSON.stringify(portrait));

  // Leaving the stage must return to the same vertical position, not the top.
  await page.evaluate(()=>{if(typeof window.lvStop==='function')window.lvStop()});
  await page.waitForFunction(()=>document.querySelector('#lv').hidden,{timeout:10000});
  await page.waitForTimeout(450);
  const restored=await page.evaluate(()=>window.scrollY);
  check('leaving stage restores the previous setup scroll position',Math.abs(restored-expectedScroll)<12,JSON.stringify({expectedScroll,restored}));

  // Keep the established horizontal geometry regression test.
  await page.evaluate(()=>window.lvStart());
  await page.waitForFunction(()=>!document.querySelector('#lv').hidden,{timeout:10000});
  await page.setViewportSize({width:1536,height:691});
  await page.evaluate(()=>{window.dispatchEvent(new Event('orientationchange'));window.dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(650);
  const layout=await page.evaluate(()=>{
   const rect=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return{x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),display:c.display,overflowX:c.overflowX,overflowY:c.overflowY,grid:c.gridTemplateRows}};
   return{card:rect('#lv>.card:not(.stage)'),bq:rect('#bq'),list:rect('#bq>.bsl:not([hidden])'),rows:document.querySelectorAll('#bq>.bsl:not([hidden])>.bi').length};
  });
  const l=layout.list;
  check('landscape beat selector remains visible and horizontally scrollable',!!l&&l.h>=90&&l.w>160&&l.display!=='none'&&l.overflowX==='auto'&&await page.evaluate(()=>{const e=document.querySelector('#bq>.bsl:not([hidden])');return !!e&&e.scrollWidth>e.clientWidth}),JSON.stringify(layout));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.n+(x.d?' — '+x.d:''));for(const x of fail)console.log('FAIL '+x.n+(x.d?' — '+x.d:''));console.log('V62_RESULT '+pass.length+' passed; '+fail.length+' failed');
 if(fail.length||errors.length){for(const e of errors)console.log('JS_ERROR '+e);process.exit(1)}
})().catch(e=>{console.error(e);process.exit(1)});
