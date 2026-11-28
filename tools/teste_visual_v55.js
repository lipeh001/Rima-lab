#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['V55 patch present',h.includes('rimalab-final-ui-fixes-v55')&&h.includes('rimalab-player-track-category-v55')],
 ['subtitle resolves category from active track key',h.includes('String(zKey(row))===key')&&h.includes('function activeCategory()')],
 ['favorite hearts share one active color rule',h.includes('#bp [data-rima-fav].on,#bq [data-rima-fav].on,#bbq [data-rima-fav].on')],
 ['step 2 overflow is not clipped',h.includes('#train-step-2{box-sizing:border-box!important;min-width:0!important;max-width:100%!important;overflow:visible!important')],
 ['landscape navigation hidden only during live stage',h.includes('body.rima-live-landscape nav{display:none!important')],
 ['rhyme tip spacing added',h.includes('#lv:not([hidden]) #stg.stage .v3bar{margin-top:12px!important')],
 ['version 3.3.4/code76',/versionCode\s*=\s*76/.test(g)&&/versionName\s*=\s*["']3\.3\.4["']/.test(g)]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)bad++}
if(bad)process.exit(1);
