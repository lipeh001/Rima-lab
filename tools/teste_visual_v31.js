#!/usr/bin/env node
const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8'),g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
['ticker marquee do player',h.includes('rimalab-player-stage-runtime-v31')&&h.includes('rimaV31Marquee')],
['favorito do player identifica beat atual',h.includes('function currentTrack()')&&h.includes('rimaV29ToggleFav(cur.key)')],
['favoritos do player e catálogo compartilham chave',h.includes("rimalab_favorites_v29")&&h.includes('data-rima-fav')],
['barra horizontal fixada na parte inferior',h.includes('#pbar{position:fixed!important;top:auto!important;transform:none!important}')&&h.includes('bottom:calc(10px')],
['progresso pausa junto com áudio',h.includes('p.dataset.rimaPlaying=String(playing)')&&h.includes("addEventListener(ev,audioState)")],
['dicas e palavras reposicionadas',h.includes("setProperty('bottom','68px'")&&h.includes("setProperty('margin-top','14px'")],
['botão aleatório removido da barra de favoritos',h.includes('/beat aleatório/i.test(clean(b.textContent))')],
['botão favoritos centralizado',h.includes("setProperty('justify-content','center','important')")],
['versão 3.1.1',g.includes('versionCode 53')&&g.includes('3.1.1')]
];let bad=0;for(const [n,ok] of checks){console.log((ok?'PASS ':'FAIL ')+n);if(!ok)bad++}if(bad)process.exit(1);
