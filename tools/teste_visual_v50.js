#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gradlePath=['app/build.gradle','app/build.gradle.kts'].map(x=>path.join(root,x)).find(fs.existsSync);
if(!gradlePath)throw Error('Gradle file missing');
const gradle=fs.readFileSync(gradlePath,'utf8');
const pass=[],fail=[],errors=[];
const ok=(name,condition,detail='')=>(condition?pass:fail).push({name,detail});
const shim='<script>(()=>{const m=new Map();Object.defineProperty(window,"localStorage",{configurable:true,value:{getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(k),clear:()=>m.clear()}});window.RimaNative={baixar:(k,url,perm)=>{window.__download={key:k,url,perm}},apagar:k=>{window.__delete=k},lista:()=>"[]"}})()</script>';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent(shim+html,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>{const e=document.querySelector('#rima-splash');return !e||e.classList.contains('done')},{timeout:15000});
  await page.waitForSelector('#md .mc',{timeout:15000});
  const tap=async(selector)=>{
   const loc=page.locator(selector).first();await loc.waitFor({state:'visible',timeout:10000});
   await loc.evaluate(e=>e.scrollIntoView({block:'center',inline:'nearest'}));
   const b=await loc.boundingBox();if(!b)throw Error('No box for '+selector);
   await page.mouse.click(b.x+b.width/2,b.y+b.height/2);await page.waitForTimeout(180);
  };
  await tap('#md .mc');await tap('#train-step-1 .go');
  await page.waitForSelector('#bp .bsl .bi .mc',{timeout:15000});
  const keys=await page.evaluate(()=>{
   const all=Object.keys(ZLIB||{}).flatMap(cat=>(ZLIB[cat]&&ZLIB[cat][1]||[]).map(x=>'jm-'+String(x[4])));
   return [...new Set(all)].filter(k=>k!=='jm-undefined'&&k!=='jm-null').slice(0,24);
  });
  ok('fixture has enough tracks for a long Favorites list',keys.length>=18,'count='+keys.length);
  await page.evaluate(ids=>{localStorage.setItem('rimalab_favorites_v29',JSON.stringify(ids));window.pk()},keys);
  await page.waitForSelector('#bp .rima-v43-toggle',{timeout:8000});
  await tap('#bp .rima-v43-toggle');
  await page.waitForSelector('#bp .rima-v43-fav-row',{timeout:8000});
  const actionOrder=await page.locator('#bp .rima-v43-fav-row').first().evaluate(row=>Array.from(row.children).map(e=>e.className));
  ok('Favorites row action order is heart then download',actionOrder.length===3&&actionOrder[1].includes('rima-v43-fav-heart')&&actionOrder[2].includes('rima-v47-fav-download'),JSON.stringify(actionOrder));
  const before=await page.evaluate(()=>{
   const rows=[...document.querySelectorAll('#bp .rima-v43-fav-row')],row=rows[rows.length-1];
   row.scrollIntoView({block:'center'});
   const r=row.getBoundingClientRect();
   return {key:row.getAttribute('data-key'),pageY:window.scrollY,rowTop:r.top,rowCount:rows.length};
  });
  ok('page can scroll vertically to a saved beat near the bottom',before.rowCount>=18&&before.pageY>0,JSON.stringify(before));
  await page.evaluate(()=>{const rows=[...document.querySelectorAll('#bp .rima-v43-fav-row')];rows[rows.length-1].querySelector('.rima-v43-fav-play').click()});
  await page.waitForTimeout(900);
  const after=await page.evaluate(k=>{
   const row=document.querySelector('#bp .rima-v43-fav-row[data-key="'+k+'"]'),r=row&&row.getBoundingClientRect();
   return {showing:!!document.querySelector('#bp>.rima-v43-favlist'),pageY:window.scrollY,rowTop:r?r.top:null,selected:ZS.key};
  },before.key);
  ok('playing a low favorite preserves the exact page/list position',after.showing&&Math.abs(after.pageY-before.pageY)<=3&&after.rowTop!=null&&Math.abs(after.rowTop-before.rowTop)<=8&&after.selected===before.key,JSON.stringify({before,after}));
  await tap('#bp .rima-v43-toggle');
  const remains=await page.evaluate(()=>({showing:!!document.querySelector('#bp>.rima-v43-favlist'),pressed:document.querySelector('#bp .rima-v43-toggle')?.getAttribute('aria-pressed'),saved:JSON.parse(localStorage.getItem('rimalab_favorites_v29')||'[]').length}));
  ok('tapping selected Favorites again leaves it selected',remains.showing&&remains.pressed==='true'&&remains.saved>=18,JSON.stringify(remains));
  await tap('#bp .rima-v50-category-row .tag.chip:first-child');
  const setupBack=await page.evaluate(()=>({mode:!!document.querySelector('#bp>.rima-v43-favlist'),category:ZS.s,visible:!document.querySelector('#bp>.bsl').hidden}));
  ok('category chip is the action that switches out of Favorites',!setupBack.mode&&setupBack.category==='Boom bap'&&setupBack.visible,JSON.stringify(setupBack));

  await tap('#train-step-2 .training-footer .go');
  await page.waitForFunction(()=>!document.querySelector('#lv').hidden,{timeout:12000});
  await page.waitForSelector('#bq .rima-v43-toggle',{timeout:8000});
  const portraitWord=await page.evaluate(()=>{
   const stage=document.querySelector('#stg.stage'),word=document.querySelector('#stg #cb');
   const a=stage.getBoundingClientRect(),b=word.getBoundingClientRect();
   return {stageCenter:a.top+a.height/2,wordCenter:b.top+b.height/2,stageHeight:a.height,wordHeight:b.height,display:getComputedStyle(word).display,flex:getComputedStyle(word).flex};
  });
  ok('portrait palco gives the main word a centered flexible region',portraitWord.stageHeight>350&&portraitWord.wordHeight>=100&&Math.abs(portraitWord.wordCenter-portraitWord.stageCenter)<135,JSON.stringify(portraitWord));

  await tap('#bq .rima-v43-toggle');
  await page.waitForSelector('#bq .rima-v43-fav-row',{timeout:8000});
  const liveOrder=await page.locator('#bq .rima-v43-fav-row').first().evaluate(row=>Array.from(row.children).map(e=>e.className));
  ok('live Favorites also uses heart then download order',liveOrder.length===3&&liveOrder[1].includes('rima-v43-fav-heart')&&liveOrder[2].includes('rima-v47-fav-download'),JSON.stringify(liveOrder));
  await tap('#bq .rima-v43-toggle');
  const liveRemains=await page.evaluate(()=>({showing:!!document.querySelector('#bq>.rima-v43-favlist'),pressed:document.querySelector('#bq .rima-v43-toggle')?.getAttribute('aria-pressed')}));
  ok('live Favorites remains selected on a second tap',liveRemains.showing&&liveRemains.pressed==='true',JSON.stringify(liveRemains));
  await tap('#bq .rima-v50-category-row .tag.chip:first-child');

  // Match the real use case: the persistent player is visible while audio is playing.
  await page.evaluate(()=>document.body.classList.add('pl','rima-player-visible'));
  await page.setViewportSize({width:1536,height:691});
  await page.evaluate(()=>{window.dispatchEvent(new Event('orientationchange'));window.dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(450);
  const horizontal=await page.evaluate(()=>{
   const rect=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
   const card=document.querySelector('#bq')?.closest('.card'),row=document.querySelector('#bq>.rima-v50-category-row');
   const chips=row?[...row.querySelectorAll('.tag.chip')].map(e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,visible:r.width>0&&getComputedStyle(e).display!=='none'}}):[];
   const bar=document.querySelector('#bq>.rima-v43-tools button'),br=bar&&bar.getBoundingClientRect();
   const p=document.getElementById('pbar');
   return {
    htmlWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,mainWidth:document.querySelector('main').scrollWidth,viewport:innerWidth,
    htmlOverflow:getComputedStyle(document.documentElement).overflowX,bodyOverflow:getComputedStyle(document.body).overflowX,bodyTouch:getComputedStyle(document.body).touchAction,
    locked:document.body.classList.contains('rima-live-landscape')&&document.documentElement.classList.contains('rima-live-landscape'),
    card:rect('#bq')&&rect('#bq').width?(()=>{const r=card.getBoundingClientRect();return{x:r.x,right:r.right,top:r.top,bottom:r.bottom}})():null,
    lv:rect('#lv'),stage:rect('#stg.stage'),stop:rect('#lv>.btn.w'),
    bq:rect('#bq'),categoryRow:rect('#bq>.rima-v50-category-row'),chips,favoritesButton:br&&{left:br.left,right:br.right,width:br.width},
    list:rect('#bq>.bsl'),player:rect('#pbar'),row:rect('#pbar .pwrow'),info:rect('#pbar .pwinfo'),seek:rect('#pbar .pwscr'),
    playerHeight:p.getBoundingClientRect().height,playerCount:document.querySelectorAll('#pbar').length
   };
  });
  ok('landscape page is locked against side-drag but retains vertical list movement',
    horizontal.locked&&horizontal.htmlOverflow==='hidden'&&horizontal.bodyOverflow==='hidden'&&horizontal.bodyTouch==='pan-y'&&horizontal.htmlWidth<=horizontal.viewport+1&&horizontal.bodyWidth<=horizontal.viewport+1&&horizontal.mainWidth<=horizontal.viewport+1,
    JSON.stringify(horizontal));
  const chipBounds=horizontal.chips.every(c=>c.visible&&c.width>0&&horizontal.card&&c.left>=horizontal.card.x-1&&c.right<=horizontal.card.right+1);
  ok('all Boom bap / Trap / Drill buttons fit inside the landscape panel',horizontal.chips.length>=3&&chipBounds,JSON.stringify(horizontal.chips));
  ok('Favorites button is fully visible below the categories',!!horizontal.favoritesButton&&horizontal.categoryRow&&horizontal.favoritesButton.left>=horizontal.card.x-1&&horizontal.favoritesButton.right<=horizontal.card.right+1&&horizontal.favoritesButton.width>200,JSON.stringify(horizontal.favoritesButton));
  ok('catalog occupies a separate vertical-scroll region',!!horizontal.list&&horizontal.list.height>70&&horizontal.list.bottom<=horizontal.card.bottom+1,JSON.stringify(horizontal.list));
  ok('stage and stop button remain above the same landscape player dock',
    !!horizontal.stage&&!!horizontal.stop&&!!horizontal.player&&
    horizontal.stage.bottom<=horizontal.player.y-4&&horizontal.stop.bottom<=horizontal.player.y-4,
    JSON.stringify({stage:horizontal.stage,stop:horizontal.stop,player:horizontal.player,lv:horizontal.lv}));
  ok('landscape time label sits between controls and progress row without overlap',
    horizontal.playerHeight>=82&&horizontal.row&&horizontal.info&&horizontal.seek&&horizontal.row.bottom<=horizontal.info.y+1&&horizontal.info.bottom<=horizontal.seek.y+1&&horizontal.seek.bottom<=horizontal.player.bottom+1,
    JSON.stringify({player:horizontal.player,row:horizontal.row,info:horizontal.info,seek:horizontal.seek}));
  ok('there is only one persistent player node',horizontal.playerCount===1);

  const playerNode=await page.evaluate(()=>{window.__rimaV50LandscapePlayer=document.getElementById('pbar');return document.getElementById('pbar').innerHTML});
  await page.setViewportSize({width:393,height:852});
  await page.evaluate(()=>{window.dispatchEvent(new Event('orientationchange'));window.dispatchEvent(new Event('resize'))});
  await page.waitForTimeout(700);
  const returned=await page.evaluate(()=>({same:document.getElementById('pbar')===window.__rimaV50LandscapePlayer,count:document.querySelectorAll('#pbar').length,height:document.getElementById('pbar').getBoundingClientRect().height,style:document.getElementById('pbar').getAttribute('style'),html:document.getElementById('pbar').innerHTML}));
  ok('portrait restores the original player node and controls',returned.same&&returned.count===1&&returned.html===playerNode&&Math.abs(returned.height-116)<=2&&!/(position|top|bottom|left|right|height|min-height|max-height|z-index):/.test(returned.style||''),JSON.stringify({height:returned.height,style:returned.style,same:returned.same}));
  ok('version 3.2.9 / code 71',/versionCode\s*=\s*71|versionCode\s+71/.test(gradle)&&/versionName\s*=\s*['"]3\.2\.9['"]|versionName\s+['"]3\.2\.9['"]/.test(gradle));
  ok('no uncaught JavaScript errors',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' :: '+x.detail:''));
 for(const x of fail)console.log('FAIL '+x.name+(x.detail?' :: '+x.detail:''));
 console.log(pass.length+' passed / '+fail.length+' failed');
 if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
