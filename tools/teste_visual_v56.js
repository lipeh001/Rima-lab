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
check('runtime SVG do coração',h.includes('rimalab-centered-heart-runtime-v56')&&h.includes("setAttribute('viewBox','0 0 24 24')"));
check('SVG acompanha mudanças de estado',h.includes("existing.setAttribute('data-filled',on?'true':'false')")&&h.includes("attributeFilter:['class','aria-pressed']")&&h.includes('characterData:true'));
check('passo 2 tem recuo dos dois lados',h.includes('padding:0 6px!important')&&h.includes('padding:6px 9px 8px!important'));
check('seletor vertical reserva área útil',h.includes('min-height:min(20vh,175px)!important')&&h.includes('max-height:min(26vh,220px)!important'));
check('lista horizontal tem faixa própria',h.includes('grid-template-columns:minmax(0,1fr) 88px!important')&&h.includes('grid-template-rows:30px 12px minmax(0,1fr)!important'));
check('dica horizontal fica dentro do palco',h.includes('margin:auto auto 1px!important')&&h.includes('overflow:hidden!important'));
const runtime=h.match(/<script\b[^>]*id=["']rimalab-centered-heart-runtime-v56["'][^>]*>([\s\S]*?)<\/script>/);
check('script vetorial pode ser isolado para teste',!!runtime);
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage({viewport:{width:360,height:640}});
  page.on('pageerror',e=>errors.push(String(e)));
  const fixture='<!doctype html><html><body><button id="heart" class="rima-v43-fav-heart on" aria-pressed="true">♥</button><script>'+runtime[1]+'</script></body></html>';
  await page.setContent(fixture,{waitUntil:'domcontentloaded',timeout:10000});
  await page.waitForFunction(()=>document.querySelector('#heart svg.rima-heart-icon')?.getAttribute('data-filled')==='true',{timeout:3000});
  check('SVG inicia preenchido para favorito ativo',true);
  await page.evaluate(()=>{const b=document.querySelector('#heart');b.classList.remove('on');b.setAttribute('aria-pressed','false');b.textContent='♡'});
  await page.waitForFunction(()=>document.querySelector('#heart svg.rima-heart-icon')?.getAttribute('data-filled')==='false',{timeout:3000});
  check('SVG fica vazado ao remover dos favoritos',true);
  await page.evaluate(()=>{const b=document.querySelector('#heart');b.classList.add('on');b.setAttribute('aria-pressed','true');b.textContent='♥'});
  await page.waitForFunction(()=>document.querySelector('#heart svg.rima-heart-icon')?.getAttribute('data-filled')==='true',{timeout:3000});
  check('SVG volta a preencher ao favoritar',true);
  const dims=await page.evaluate(()=>{const r=document.querySelector('#heart svg.rima-heart-icon').getBoundingClientRect();return [r.width,r.height]});
  check('SVG mantém proporção quadrada de 20px',dims[0]===20&&dims[1]===20,JSON.stringify(dims));
  check('sem exceções JavaScript',errors.length===0,errors.join(' | '));
 }finally{await browser.close()}
 for(const x of pass)console.log('PASS '+x.name+(x.detail?' — '+x.detail:''));
 for(const x of fail)console.log('FAIL '+x.name+(x.detail?' — '+x.detail:''));
 console.log('V56_RESULT '+pass.length+' passed; '+fail.length+' failed');
 if(fail.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
