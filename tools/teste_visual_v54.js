#!/usr/bin/env node
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const root=path.resolve(process.argv[2]),html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gp=['app/build.gradle','app/build.gradle.kts'].map(p=>path.join(root,p)).find(fs.existsSync),gradle=fs.readFileSync(gp,'utf8');
const pass=[],fail=[],errors=[],ok=(n,c,d='')=>(c?pass:fail).push({name:n,detail:d});
const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(String(k)),clear:()=>m.clear()}});window.RimaNative={baixar:()=>{},apagar:()=>{},lista:()=>"[]",mediaState:()=>{}}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>{const s=document.querySelector('#rima-splash');return !s||s.classList.contains('done')},{timeout:15000});
  const click=async s=>{const x=page.locator(s).first();await x.waitFor({state:'visible',timeout:10000});await x.scrollIntoViewIfNeeded();await x.click({timeout:10000});await page.waitForTimeout(120)};
  const getFav=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]'));
  const tapCount=()=>page.evaluate(()=>window.__v54ZlpCalls||0);
  await page.waitForSelector('#train-step-1 .go',{timeout:12000});
  await click('#md .mc');await click('#train-step-1 .go');
  await page.waitForFunction(()=>!document.querySelector('#train-step-2').hidden,{timeout:8000});
  const setup=await page.evaluate(()=>({lists:document.querySelectorAll('#bp>.bsl').length,max:getComputedStyle(document.querySelector('#bp>.bsl')).maxHeight,overflow:getComputedStyle(document.querySelector('#bp>.bsl')).overflowY,player:getComputedStyle(document.querySelector('#pbar')).display}));
  ok('stage 2 has exactly one bounded, scrollable list',setup.lists===1&&setup.max!=='none'&&setup.overflow==='auto',JSON.stringify(setup));
  ok('player stays hidden in stage 2',setup.player==='none'||setup.player==='');
  await page.evaluate(async()=>{if(window.rimaCatalogReady&&typeof window.rimaCatalogReady.then==='function')await window.rimaCatalogReady});
  await page.waitForFunction(()=>Array.isArray(window.ZLIB?.['Boom bap']?.[1])&&window.ZLIB['Boom bap'][1].length>1&&!!document.querySelector('#bp .bsl .bi .mc'),{timeout:15000});
  await page.evaluate(()=>{window.__v54ClickSelector=null;window.__v54ClickCount=0;document.addEventListener('click',e=>{const s=window.__v54ClickSelector;if(s&&e.target.closest&&e.target.closest(s))window.__v54ClickCount++},true)});
  const selectedBefore=await page.evaluate(()=>ZS.key||'');
  const firstCatalogButton=page.locator('#bp .bsl .bi .mc').nth(selectedBefore?1:0);
  const expectedClick=await firstCatalogButton.getAttribute('onclick');
  const expectedMatch=String(expectedClick||'').match(/zLP\((\d+),0,'([^']+)'\)/);
  if(!expectedMatch)throw new Error('Catalog play button has no valid one-track handler');
  const expectedKey=await page.evaluate(({i,cat})=>'jm-'+String(ZLIB[cat][1][i][4]),{i:Number(expectedMatch[1]),cat:expectedMatch[2]});
  await page.evaluate(s=>{window.__v54ClickSelector=s;window.__v54ClickCount=0},'#bp .bsl .bi .mc');
  await firstCatalogButton.click({timeout:10000});
  await page.waitForFunction(k=>ZS.key===k,expectedKey,{timeout:6000});
  const key=await page.evaluate(()=>ZS.key);
  const catalogClicks=await page.evaluate(()=>window.__v54ClickCount);
  ok('one catalog tap selects the requested beat without duplicating the list',key===expectedKey&&catalogClicks===1&&document.querySelectorAll('#bp>.bsl').length===1,JSON.stringify({key,expectedKey,catalogClicks}));
  await page.locator('#bp .bsl .bi [data-rima-fav]').first().waitFor({state:'visible',timeout:8000});
  await click('#bp .bsl .bi [data-rima-fav]');
  await page.waitForFunction(k=>JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]').includes(k),key,{timeout:5000});
  await page.waitForTimeout(180);
  const heartSync=await page.evaluate(k=>['bp','bq'].every(id=>[...document.querySelectorAll('#'+id+' [data-rima-fav]')].some(b=>b.getAttribute('data-rima-fav')===k&&b.classList.contains('on'))),key);
  ok('favorite status synchronizes across setup, live and battle catalogs',heartSync);
  await click('#bp .rima-v43-toggle');await page.locator('#bp .rima-v43-fav-row').first().waitFor({state:'visible',timeout:8000});
  const shape=await page.locator('#bp .rima-v43-fav-row').first().evaluate(r=>({bi:r.classList.contains('bi'),info:!!r.querySelector('.beat-info'),title:!!r.querySelector('.beat-info .mc b'),artist:!!r.querySelector('.beat-meta .beat-artist'),heart:!!r.querySelector('.rima-v43-fav-heart'),download:!!r.querySelector('.dlb'),lists:document.querySelectorAll('#bp>.rima-v43-favlist').length,hidden:document.querySelector('#bp>.bsl')?.hidden}));
  ok('Favorites cards use the catalog card structure and styling',shape.bi&&shape.info&&shape.title&&shape.artist&&shape.heart&&shape.download,JSON.stringify(shape));
  ok('Favorites shows one list and hides the original catalog',shape.lists===1&&shape.hidden===true,JSON.stringify(shape));
  await page.evaluate(()=>{window.__v54ClickSelector='#bp .rima-v43-fav-play';window.__v54ClickCount=0});
  await click('#bp .rima-v43-fav-play');await page.waitForFunction(k=>ZS.key===k,key,{timeout:6000});
  const favoriteClicks=await page.evaluate(()=>window.__v54ClickCount);
  ok('one tap on a favorite starts the selected beat without duplicate clicks',await page.evaluate(()=>ZS.key)===key&&favoriteClicks===1,String(favoriteClicks));
  await click('#bp .rima-v43-fav-heart');await page.waitForFunction(k=>!JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]').includes(k),key,{timeout:5000});
  ok('heart inside Favorites removes the track from shared saved state',!(await getFav()).includes(key));
  await click('#bp .row .tag.chip');
  for(const category of ['Boom bap','Trap','Drill']){
   await page.locator('#bp .row .tag.chip').filter({hasText:category}).first().click({timeout:10000});
   await page.waitForFunction(c=>ZS.s===c,category,{timeout:5000});
   await page.evaluate(()=>{window.__v54ClickSelector='#bp .bsl .bi .mc';window.__v54ClickCount=0});
   const catButton=page.locator('#bp .bsl .bi .mc').first();
   const catHandler=String(await catButton.getAttribute('onclick')||'').match(/zLP\((\d+),0,'([^']+)'\)/);
   const catKey=catHandler?await page.evaluate(({i,cat})=>'jm-'+String(ZLIB[cat][1][i][4]),{i:Number(catHandler[1]),cat:catHandler[2]}):'';
   await catButton.click({timeout:10000});if(catKey)await page.waitForFunction(k=>ZS.key===k,catKey,{timeout:5000});
   const n=await page.evaluate(()=>window.__v54ClickCount),cat=await page.evaluate(()=>ZS.s);
   ok('category '+category+' responds to one playback tap',cat===category&&!!catKey&&n===1,JSON.stringify({cat,n,catKey}));
  }
  await click('#train-step-2 .training-footer .go');await page.waitForFunction(()=>!document.querySelector('#lv').hidden,{timeout:12000});
  const liveList=await page.evaluate(()=>({count:document.querySelectorAll('#bq>.bsl').length,max:getComputedStyle(document.querySelector('#bq>.bsl')).maxHeight,overflow:getComputedStyle(document.querySelector('#bq>.bsl')).overflowY}));
  ok('live stage also has one bounded list',liveList.count===1&&liveList.max!=='none'&&liveList.overflow==='auto',JSON.stringify(liveList));
  await click('#bq .bsl .bi .mc');await page.waitForTimeout(250);
  const liveKey=await page.evaluate(()=>ZS.key);
  await click('#bq .bsl .bi [data-rima-fav]');
  await page.waitForFunction(k=>JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]').includes(k),liveKey,{timeout:5000});
  // Mimic the audio engine's active-playback notification after the actual beat-selection tap.
  await page.evaluate(()=>zSetPL(1));await page.waitForTimeout(250);
  const player=await page.evaluate(()=>({visible:getComputedStyle(document.querySelector('#pbar')).display!=='none'&&getComputedStyle(document.querySelector('#pbar')).visibility!=='hidden',gate:document.body.classList.contains('rima-v51-player-eligible'),stage:!document.querySelector('#lv').hidden}));
  ok('player gate opens for active playback only inside the live stage',player.visible&&player.gate&&player.stage,JSON.stringify(player));
  await click('#bq .rima-v43-toggle');await page.locator('#bq .rima-v43-fav-row').first().waitFor({state:'visible',timeout:8000});
  ok('Favorites works in the live selector without duplicating the list',await page.locator('#bq>.rima-v43-favlist').count()===1&&await page.locator('#bq>.bsl[hidden]').count()===1);
  await click('#bq .row .tag.chip');
  await click('#lv .bk');await page.waitForFunction(()=>document.querySelector('#lv').hidden,{timeout:10000});
  const off=await page.evaluate(()=>({hidden:getComputedStyle(document.querySelector('#pbar')).display==='none',step2:!document.querySelector('#train-step-2').hidden}));
  ok('leaving the live stage hides the player and returns to setup',off.hidden&&off.step2,JSON.stringify(off));

  await click('nav button[data-i="2"]');await page.waitForSelector('#bt .hero',{timeout:8000});await click('#bt button.mc');await page.waitForSelector('#bbq>.bsl',{timeout:10000});
  const battle=await page.evaluate(()=>({lists:document.querySelectorAll('#bbq>.bsl').length,toggle:!!document.querySelector('#bbq .rima-v43-toggle'),hearts:document.querySelectorAll('#bbq .bsl [data-rima-fav]').length}));
  ok('Battle opens with one catalog and shared Favorites control',battle.lists===1&&battle.toggle&&battle.hearts>0,JSON.stringify(battle));
  const bkey=await page.locator('#bbq .bsl .bi .mc').first().getAttribute('data-rima-track-key');
  await click('#bbq .bsl .bi [data-rima-fav]');await page.waitForFunction(k=>JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]').includes(k),bkey,{timeout:5000});
  await click('#bbq .rima-v43-toggle');await page.locator('#bbq .rima-v43-fav-row').first().waitFor({state:'visible',timeout:8000});
  ok('Battle Favorites reuses the same catalog card',await page.locator('#bbq .rima-v43-fav-row.bi .beat-info').count()>0);
  await click('#bbq .rima-v43-fav-play');
  ok('Battle favorite playback selects the matching track',await page.evaluate(k=>ZS.key===k,bkey));
  await click('#bbq .row .tag.chip');
  const startButton=page.getByRole('button',{name:'Começar batalha'});
  await startButton.waitFor({state:'visible',timeout:8000});
  await startButton.click({timeout:10000});
  await page.waitForFunction(()=>!!B&&!!document.querySelector('#bt .card.stage'),{timeout:6000}).catch(()=>{});
  const battleState=await page.evaluate(()=>({hasBattle:typeof B!=='undefined'&&!!B,stage:!!document.querySelector('#bt .card.stage'),roundText:document.querySelector('#bt .card.stage')?.innerText||'',startButton:document.querySelector('#bt button.btn.go')?.outerHTML||'',errors:window.__v54Errors||[]}));
  const battleStarted=battleState.hasBattle&&battleState.stage;
  ok('Começar batalha opens the live battle stage',battleStarted,JSON.stringify(battleState));
  if(battleStarted){await click('#bt .card.stage button.btn');ok('Valendo starts the battle round',await page.evaluate(()=>!!B&&B.run===1))}

  await click('nav button[data-i="1"]');await page.waitForFunction(()=>!document.querySelectorAll('.tab')[1].hidden,{timeout:7000});
  await page.locator('#al details summary').first().click({timeout:8000});await click('#al details button');
  const aula=await page.evaluate(()=>!document.querySelector('#lv').hidden);
  ok('Aulas live-training action starts its lesson',aula);
  if(aula){await click('#lv .bk');await page.waitForFunction(()=>document.querySelector('#lv').hidden,{timeout:10000})}

  await click('nav button[data-i="0"]');await page.waitForFunction(()=>!document.querySelector('#train-step-2').hidden,{timeout:8000});
  await page.setViewportSize({width:852,height:393});await page.evaluate(()=>{dispatchEvent(new Event('orientationchange'));dispatchEvent(new Event('resize'))});await page.waitForTimeout(450);
  const wide=await page.evaluate(()=>({lists:document.querySelectorAll('#bp>.bsl').length,max:getComputedStyle(document.querySelector('#bp>.bsl')).maxHeight,overflow:getComputedStyle(document.querySelector('#bp>.bsl')).overflowY}));
  ok('landscape stage 2 has one bounded scrollable catalog',wide.lists===1&&wide.max!=='none'&&wide.overflow==='auto',JSON.stringify(wide));
  const wideRows=page.locator('#bp .bsl .bi');
  const wideCount=await wideRows.count();
  const wideTarget=await page.evaluate(()=>{const saved=new Set(JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]'));const rows=[...document.querySelectorAll('#bp .bsl .bi')];for(let i=0;i<rows.length;i++){const heart=rows[i].querySelector('[data-rima-fav]');if(heart&&!saved.has(heart.getAttribute('data-rima-fav')))return i}return -1});
  if(wideTarget>=0){await page.locator('#bp .bsl .bi').nth(wideTarget).locator('[data-rima-fav]').click({timeout:10000});}
  const wideFav=await page.evaluate(()=>({count:JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]').length,heart:wideTarget>=0?document.querySelectorAll('#bp .bsl .bi [data-rima-fav]')[wideTarget]?.getAttribute('aria-pressed'):null,target:wideTarget,wideCount}));
  ok('landscape one-tap favorite updates the shared state',wideTarget>=0&&wideFav.count>0&&wideFav.heart==='true',JSON.stringify(wideFav));
  ok('version 3.3.3 / code 75',/versionCode\s*=\s*75|versionCode\s+75/.test(gradle)&&/versionName\s*=\s*['"]3\.3\.3['"]|versionName\s+['"]3\.3\.3['"]/.test(gradle));
  ok('V53 global scrolling is preserved',html.includes('rimalab-global-scroll-system-v53'));
  ok('no uncaught JavaScript errors',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' :: '+x.detail:''));for(const x of fail)console.log('FAIL '+x.name+(x.detail?' :: '+x.detail:''));console.log(pass.length+' passed / '+fail.length+' failed');if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
