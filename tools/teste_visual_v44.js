#!/usr/bin/env node
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gp=['app/build.gradle','app/build.gradle.kts'].map(p=>path.join(root,p)).find(fs.existsSync);
if(!gp)throw new Error('Gradle file missing');
const g=fs.readFileSync(gp,'utf8');
const js=h.match(/<script id="rimalab-favorites-layout-runtime-v43">([\s\S]*?)<\/script>/)?.[1]||'';
const css=h.match(/<style id="rimalab-favorites-catalog-lexical-v44">([\s\S]*?)<\/style>/)?.[1]||'';
const cat=js.match(/const catalog=\(\)=>[^;]+;/)?.[0]||'';
const checks=[];
function check(name,ok){checks.push([name,!!ok])}
check('V43 Favorites runtime retained',!!js&&h.includes('rimalab-favorites-layout-v43'));
check('catalog resolver reads lexical ZLIB before window fallback',cat.includes("typeof ZLIB!=='undefined'&&ZLIB")&&cat.includes('(window.ZLIB||{})'));
check('broken window-only catalog access removed',!cat.includes('()=>window.ZLIB||{}'));
check('the same Favorites storage key is retained',js.includes("const KEY='rimalab_favorites_v29'"));
check('stored favorite IDs are not cleared or migrated destructively',!h.includes("removeItem('rimalab_favorites_v29')"));
check('both selector roots remain supported',js.includes("ids=['bp','bq']")&&js.includes('#bp .rima-v43-toggle,#bq .rima-v43-toggle'));
check('favorite titles remain clickable',js.includes('data-v43-play')&&js.includes('#bp [data-v43-play],#bq [data-v43-play]'));
check('individual hearts remain removable',js.includes('data-v43-heart')&&js.includes('window.rimaV29ToggleFav(key)'));
check('V41 favorite playlist remains the playback target',js.includes('window.rimaV41StartFavorites||window.rimaV29PlayFav'));
check('list rows and hearts retain touch interaction',css.includes('touch-action:manipulation!important')&&css.includes('pointer-events:auto!important'));
check('version 3.2.2 / code 64',/versionCode\s*=\s*64|versionCode\s+64/.test(g)&&/versionName\s*=\s*['"]3\.2\.2['"]|versionName\s+['"]3\.2\.2['"]/.test(g));
if(cat){
 const sample={'Boom bap':[92,[['u1','Favorite one',90,0,'101'],['u2','Favorite two',92,0,'102']]],'Trap':[140,[['u3','Favorite three',140,0,'201']]],'Drill':[142,[['u4','Favorite four',142,0,'301']]]};
 const probe='const ZLIB='+JSON.stringify(sample)+'; const window={}; '+cat+' const saved=new Set(["jm-101","jm-102","jm-201","jm-301"]); const items=Object.keys(catalog()).flatMap(cat=>(catalog()[cat]&&catalog()[cat][1]||[]).map((x,i)=>({cat,x,i,key:"jm-"+String(x[4])})).filter(t=>t.key!=="jm-")).filter(t=>saved.has(t.key)); JSON.stringify({keys:Object.keys(catalog()),items:items.map(t=>t.key)});';
 let parsed=null,err=null;
 try{parsed=JSON.parse(vm.runInNewContext(probe,{}))}catch(e){err=e}
 check('Android-like lexical ZLIB resolves when window.ZLIB is absent',!err&&parsed&&parsed.keys.length===3);
 check('all four stored sample favorites resolve to actual catalog beats',!err&&parsed&&parsed.items.length===4&&parsed.items.join(',')==='jm-101,jm-102,jm-201,jm-301');
}else{
 check('catalog resolver is available for runtime simulation',false);
 check('all four stored sample favorites resolve to actual catalog beats',false);
}
let failures=0;
for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)failures++}
if(failures)process.exit(1);
console.log(checks.length+'/'+checks.length+' V44 checks passed');
