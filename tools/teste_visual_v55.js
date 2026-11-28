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
 ['version 3.3.5/code77',/versionCode\s*(?:=\s*)?77/.test(g)&&/versionName\s*(?:=\s*)?["']3\.3\.5["']/.test(g)],
 ['V56 SVG heart runtime',h.includes('rimalab-heart-svg-runtime-v56')&&h.includes("setAttribute('viewBox','0 0 24 24')")],
 ['V56 step2 inset prevents left crop',h.includes('#train-step-2 #bp{padding:0 3px!important;overflow-x:hidden!important')&&h.includes('padding:6px 7px 7px!important')],
 ['V56 compact favorite titles',h.includes('padding:7px 10px 6px!important;line-height:1.1!important')&&h.includes('-webkit-line-clamp:2!important')],
 ['V56 portrait selector expands like step2',h.includes('max-height:min(40vh,340px)!important')&&h.includes('min-height:min(24vh,185px)!important')],
 ['V56 vertical rhyme-tip spacing',h.includes('#stg.stage #cs:not(:empty){margin:14px auto 18px!important')&&h.includes('#stg.stage .v3bar{margin:18px auto 5px!important')],
 ['V56 restores three landscape grid rows',h.includes('grid-template-rows:42px minmax(0,1fr) 42px!important')],
 ['V56 landscape beat list fills right panel',h.includes('flex:1 1 0%!important;width:100%!important;min-width:0!important;min-height:78px!important')],
 ['V56 safe landscape stage contains tip',h.includes('overflow:hidden!important;padding:clamp(9px,1.5vh,16px)')&&h.includes('min-height:36px!important;height:auto!important')],
 ['V56 hearts keep square 19px SVG',h.includes('.rima-heart-svg{display:block!important;flex:0 0 19px!important;width:19px!important;height:19px!important')]
];
let bad=0;for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)bad++}
if(bad)process.exit(1);
