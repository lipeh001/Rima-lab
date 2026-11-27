#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const pass=[],fail=[],errors=[];
const ok=(name,condition,detail='')=>(condition?pass:fail).push({name,detail});
const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()}});window.RimaNative={baixar:(k,url,perm)=>{window.__download={key:k,url,perm}},apagar:k=>{window.__delete=k},lista:()=>"[]"}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>{const e=document.querySelector('#rima-splash');return !e||e.classList.contains('done')},{timeout:15000});
  await page.waitForSelector('#md .mc',{timeout:15000});
  const tap=async(selector)=>{
   const loc=page.locator(selector).first();await loc.waitFor({state:'visible',timeout:9000});
   await loc.evaluate(e=>e.scrollIntoView({block:'center',inline:'center'}));
   const b=await loc.boundingBox();if(!b)throw Error('No box for '+selector);
   await page.mouse.click(b.x+b.width/2,b.y+b.height/2);await page.waitForTimeout(180);
  };
  await tap('#md .mc');await tap('#train-step-1 .go');
  // Wait for the real catalog bootstrap before clicking; otherwise a temporary
  // loading row can consume the tap while zLP is still building the category.
  await page.evaluate(async()=>{if(window.rimaCatalogReady&&typeof window.rimaCatalogReady.then==='function')await window.rimaCatalogReady});
  await page.waitForFunction(()=>Array.isArray(window.ZLIB?.['Boom bap']?.[1])&&window.ZLIB['Boom bap'][1].length>0&&!!document.querySelector('#bp .bsl .bi .mc'),{timeout:15000});
  const firstTrack=page.locator('#bp .bsl .bi .mc').first();
  await firstTrack.scrollIntoViewIfNeeded();
  await firstTrack.click({timeout:9000});
  await page.waitForFunction(()=>!!(window.ZS&&ZS.key),{timeout:7000});
  const key=await page.evaluate('ZS.key');
  if(!key)throw new Error('Clicked catalog beat did not produce a selected key');
  await page.waitForFunction(k=>ZS.key===k,key,{timeout:7000});
  await tap('#bp .bsl .bi:first-child [data-rima-fav]');
  const savedBefore=await page.evaluate("JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]')");
  ok('test favorite saved before opening Favorites',savedBefore.includes(key),JSON.stringify(savedBefore));
  const checkRoot=async(id,label)=>{
   const order=await page.locator('#'+id).evaluate(root=>{
    const children=Array.from(root.children);
    const category=children.findIndex(e=>e.classList.contains('row')&&e.querySelector('.tag.chip'));
    const toolbar=children.findIndex(e=>e.classList.contains('rima-v43-tools'));
    const fav=children.findIndex(e=>e.classList.contains('rima-v43-favlist'));
    const catalog=children.findIndex(e=>e.classList.contains('bsl'));
    return {category,toolbar,fav,catalog,catalogHidden:catalog>=0&&children[catalog].hidden};
   });
   ok(label+' shared order: category → Favorites → catalog',order.category>=0&&order.toolbar===order.category+1&&order.fav===order.toolbar+1&&order.catalog>order.fav,JSON.stringify(order));
   ok(label+' catalog is hidden while Favorites is open',order.catalogHidden,JSON.stringify(order));
  };
  await tap('#bp .rima-v43-toggle');
  await checkRoot('bp','setup selector');
  const savedAfterOpen=await page.evaluate("JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]')");
  ok('opening Favorites does not mutate favorite selection',JSON.stringify(savedAfterOpen)===JSON.stringify(savedBefore));
  await tap('#bp .rima-v43-toggle');
  await page.waitForTimeout(180);
  const stillFavorites=await page.evaluate(()=>({showing:!!document.querySelector('#bp>.rima-v43-favlist'),pressed:document.querySelector('#bp .rima-v43-toggle')?.getAttribute('aria-pressed'),hidden:document.querySelector('#bp>.bsl')?.hidden,saved:JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]')}));
  ok('tapping the selected Favorites tab again keeps it selected',stillFavorites.showing&&stillFavorites.pressed==='true'&&stillFavorites.hidden===true&&stillFavorites.saved.includes(key),JSON.stringify(stillFavorites));
  await tap('#bp .rima-v50-category-row .tag.chip:first-child');
  const backState=await page.evaluate(()=>({category:ZS.s,showing:!!document.querySelector('#bp>.rima-v43-favlist'),hidden:document.querySelector('#bp>.bsl')?.hidden,saved:JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]')}));
  ok('choosing Boom bap switches out of Favorites without removing saved beats',backState.category==='Boom bap'&&!backState.showing&&backState.hidden===false&&backState.saved.includes(key),JSON.stringify(backState));
  await tap('#train-step-2 .training-footer .go');
  await page.waitForFunction(()=>!document.querySelector('#lv').hidden,{timeout:10000});
  await page.waitForSelector('#bq .rima-v43-toggle',{timeout:8000});
  await tap('#bq .rima-v43-toggle');
  await checkRoot('bq','live selector');
  await tap('#bq .rima-v43-toggle');
  const liveStill=await page.evaluate(()=>({showing:!!document.querySelector('#bq>.rima-v43-favlist'),pressed:document.querySelector('#bq .rima-v43-toggle')?.getAttribute('aria-pressed'),hidden:document.querySelector('#bq>.bsl')?.hidden}));
  ok('live Favorites tab remains selected when tapped again',liveStill.showing&&liveStill.pressed==='true'&&liveStill.hidden===true,JSON.stringify(liveStill));
  await tap('#bq .rima-v50-category-row .tag.chip:first-child');
  const liveBack=await page.evaluate(()=>({category:ZS.s,showing:!!document.querySelector('#bq>.rima-v43-favlist'),hidden:document.querySelector('#bq>.bsl')?.hidden}));
  ok('choosing Boom bap from live Favorites restores that category',liveBack.category==='Boom bap'&&!liveBack.showing&&liveBack.hidden===false,JSON.stringify(liveBack));

  // Verify the very same #pbar node and children return to their original portrait geometry.
  const baseline=await page.evaluate(()=>{
   const p=document.getElementById('pbar');window.__rimaV49Player=p;
   document.body.classList.add('pl','rima-player-visible');
   return {html:p.innerHTML,height:p.getBoundingClientRect().height,computed:getComputedStyle(p).height,style:p.getAttribute('style')};
  });
  await page.setViewportSize({width:1536,height:691});
  await page.evaluate(()=>window.dispatchEvent(new Event('resize')));
  await page.waitForTimeout(260);
  const landscape=await page.evaluate(()=>({height:document.getElementById('pbar').getBoundingClientRect().height,style:document.getElementById('pbar').getAttribute('style')}));
  ok('landscape dock is applied to the existing player with separate timing/seek space',landscape.height>=82&&/height:\s*84px/.test(landscape.style||''),JSON.stringify(landscape));
  await page.setViewportSize({width:393,height:852});
  await page.evaluate(()=>{window.dispatchEvent(new Event('orientationchange'));window.dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(760);
  const portrait=await page.evaluate(()=>{
   const p=document.getElementById('pbar');
   return {sameNode:p===window.__rimaV49Player,count:document.querySelectorAll('#pbar').length,html:p.innerHTML,height:p.getBoundingClientRect().height,computed:getComputedStyle(p).height,style:p.getAttribute('style'),className:document.body.className};
  });
  ok('portrait returns the same player DOM and exact original controls',portrait.sameNode&&portrait.count===1&&portrait.html===baseline.html,JSON.stringify({sameNode:portrait.sameNode,count:portrait.count}));
  ok('portrait restores the original player height and removes landscape inline geometry',Math.abs(portrait.height-baseline.height)<=2&&!/(position|top|bottom|left|right|height|min-height|max-height|z-index):/.test(portrait.style||''),JSON.stringify({baseline:baseline.height,portrait:portrait.height,style:portrait.style}));
  ok('legacy V48 fake seekbar workaround is removed',!html.includes('rimalab-favorites-details-v48')&&!html.includes('rimalab-orientation-recovery-runtime-v48'));
  // Return to landscape with live stage active and confirm no scrollable setup page is exposed behind it.
  await page.setViewportSize({width:1536,height:691});
  await page.evaluate(()=>{window.dispatchEvent(new Event('orientationchange'));window.dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(350);
  const locked=await page.evaluate(()=>{
   const main=document.querySelector('main'),lv=document.getElementById('lv'),r=lv.getBoundingClientRect();
   return {class:document.body.classList.contains('rima-live-landscape'),mainPosition:getComputedStyle(main).position,mainOverflow:getComputedStyle(main).overflow,bodyOverflow:getComputedStyle(document.body).overflow,mainTop:main.scrollTop,documentTop:(document.scrollingElement?document.scrollingElement.scrollTop:0),lv:{top:r.top,bottom:r.bottom,height:r.height},height:innerHeight};
  });
  ok('landscape live stage locks the background page and covers the viewport',locked.class&&locked.mainPosition==='fixed'&&locked.mainOverflow==='hidden'&&locked.bodyOverflow==='hidden'&&locked.mainTop===0&&locked.documentTop===0&&locked.lv.top===0&&locked.lv.bottom>=locked.height-1,JSON.stringify(locked));
  ok('only one persistent player exists in both orientations',await page.locator('#pbar').count()===1);
  ok('no uncaught JavaScript errors',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' :: '+x.detail:''));
 for(const x of fail)console.log('FAIL '+x.name+(x.detail?' :: '+x.detail:''));
 console.log(pass.length+' passed / '+fail.length+' failed');
 if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
