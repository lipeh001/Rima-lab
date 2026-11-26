#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const script=h.match(/<script id="rimalab-favorites-and-stage-v40">([\s\S]*?)<\/script>/);
const css=h.match(/<style id="rimalab-stage-responsive-spacing-v40">([\s\S]*?)<\/style>/);
const b=script&&script[1]||'',c=css&&css[1]||'';
const checks=[
 ['favoritos usam ZLIB lexical, não window.ZLIB',b.includes("typeof ZLIB!=='undefined'")&&!b.includes('window.ZLIB')],
 ['estado do player usa ZS lexical, não window.ZS',b.includes("typeof ZS!=='undefined'")&&!b.includes('window.ZS')],
 ['chaves de favoritos normalizadas para jm-id',b.includes("k.startsWith('jm-')?k:'jm-'+k")&&b.includes("const keyOf=x=>x&&x[4]!=null?'jm-'+String(x[4]):''")],
 ['lista mostra todos os favoritos do catálogo',b.includes('allTracks().filter(o=>fav.includes(o.key))')],
 ['categorias continuam visíveis durante favoritos',b.includes("tools.insertAdjacentElement('afterend',view)")&&!b.includes("row.hidden=true")],
 ['toque em categoria fecha favoritos na fase capture',b.includes("document.addEventListener('click',e=>{\n  const chip")&&b.includes("},true);")&&b.includes("removeFavoritesView()")],
 ['categoria usa seleção original zLS após sair de favoritos',b.includes("closest('#bp .row .tag.chip')")&&b.includes('favoritesMode)removeFavoritesView()')],
 ['coração da playlist de favoritos atualiza e remove item',b.includes('rima-v40-fav-toggle')&&b.includes('toggleFav(heart.getAttribute')],
 ['coração do player lê ZS.key real',b.includes('const k=currentKey();if(k)toggleFav(k)')],
 ['palco mantém botão e elementos sem clipping',c.includes('overflow:visible!important')&&c.includes('.v3bar button')&&c.includes('min-height:44px')],
 ['timer e dica recebem margens separadas',c.includes('#cn{flex:0 0 auto')&&c.includes('.v3bar{')&&c.includes('margin:14px auto 2px')],
 ['altura horizontal ampliada e adaptativa',c.includes('calc(100svh - 66px)')&&c.includes('max-height:380px')],
 ['responsividade em telas estreitas',c.includes('@media(max-width:380px)')],
 ['versão 3.1.8 / code 60',g.includes('versionCode 60')&&g.includes("versionName '3.1.8'")]
];
let failures=0;for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)failures++}if(failures)process.exit(1);console.log(checks.length+'/'+checks.length+' verificações V40 passaram');
