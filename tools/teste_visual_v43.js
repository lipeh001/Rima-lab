#!/usr/bin/env node
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gp=['app/build.gradle','app/build.gradle.kts'].map(p=>path.join(root,p)).find(fs.existsSync);if(!gp)throw Error('Gradle missing');const g=fs.readFileSync(gp,'utf8');
const js=h.match(/<script id="rimalab-favorites-layout-runtime-v43">([\s\S]*?)<\/script>/)?.[1]||'';
const css=h.match(/<style id="rimalab-favorites-layout-v43">([\s\S]*?)<\/style>/)?.[1]||'';
const checks=[
 ['runtime V43 appended after V42',h.indexOf('rimalab-favorites-layout-runtime-v43')>h.indexOf('rimalab-selector-favorites-sync-v42')],
 ['shared toolbar on step selector #bp and live selector #bq',js.includes("ids=['bp','bq']")&&js.includes("ensureToolbar(root)")],
 ['legacy V42 toolbar class isolated',js.includes("bar.className='rima-v43-tools'")&&!js.includes('rima-v42-favorites-toggle')],
 ['toolbar is full-width row, not a sibling card',css.includes('#bp>.rima-v43-tools,#bq>.rima-v43-tools')&&css.includes('width:100%!important')],
 ['favorites list is full width block',css.includes('#bp>.rima-v43-favlist,#bq>.rima-v43-favlist')&&css.includes('display:block!important')],
 ['beat card uses flexible title column and fixed heart',css.includes('grid-template-columns:minmax(0,1fr) 46px')],
 ['title stays readable in max two lines',css.includes('-webkit-line-clamp:2')],
 ['heart is circular fixed 44px control',css.includes('width:44px!important')&&css.includes('height:44px!important')&&css.includes('border-radius:50%!important')],
 ['favorite data sourced from saved keys',js.includes('allTracks().filter(t=>saved.has(t.key))')],
 ['add and remove uses existing persistent favorite toggle',js.includes('window.rimaV29ToggleFav(key)')],
 ['player heart and catalog heart changes refresh view',js.includes('#bp [data-rima-fav],#rima-v29-player-heart')],
 ['favorite title plays selected beat through V41 queue',js.includes('window.rimaV41StartFavorites||window.rimaV29PlayFav')],
 ['both selectors can open and close same favorite view',js.includes('#bp .rima-v43-toggle,#bq .rima-v43-toggle')],
 ['live #bq keeps its original generated beats when Favorites closed',js.includes("else root.querySelectorAll('.bc').forEach(e=>e.hidden=false)")],
 ['#bq favorites survives beat selector rebuild',js.includes('const oldPk=window.pk')&&js.includes('render();return r')],
 ['step #bp category tap exits Favorites',js.includes('#bp .row .tag.chip')&&js.includes("setMode(false,'bp')")],
 ['empty Favorites state is actionable',js.includes('Nenhum beat favoritado ainda')],
 ['V43 refreshes when audio/player changes',js.includes('const oldBar=window.zBarUI')],
 ['small phone layout remains fixed-width safe',css.includes('@media(max-width:380px)')],
 ['version 3.2.1/code 63',/versionCode\s*=\s*63|versionCode\s+63/.test(g)&&/versionName\s*=\s*['"]3\.2\.1['"]|versionName\s+['"]3\.2\.1['"]/.test(g)]
];
let fail=0;for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)fail++}if(fail)process.exit(1);console.log(checks.length+'/'+checks.length+' V43 checks passed');
