const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8'),g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['ticker do título do beat',h.includes('rima-title-track')&&h.includes('rima-title-marquee-v33')],
 ['sincronização de coração do player e catálogo',h.includes('function syncHearts()')&&h.includes('rima-v29-player-heart')],
 ['remoção do botão aleatório na seleção',h.includes('return out.replace(/<button onclick="rimaV29Random')],
 ['player horizontal fixado embaixo',h.includes('bottom:calc(5px + env(safe-area-inset-bottom,0px))')],
 ['barra congelada quando pausado',h.includes('pausedAt!==null')],
 ['beat inicial padrão sem autoplay',h.includes("zLP(0,0,'Boom bap')")],
 ['ajuste do espaçamento de palco e catálogo',h.includes('rimalab-player-polish-v33')&&h.includes('#bp .bsl{margin:2px 0 5px')],
 ['versão 3.1.1 / code 53',g.includes('versionCode 53')&&g.includes("versionName '3.1.1'")]
];let bad=0;for(const [n,ok] of checks){console.log((ok?'PASS':'FAIL')+' '+n);if(!ok)bad++}if(bad)process.exit(1);