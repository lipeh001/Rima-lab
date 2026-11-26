const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8'),g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
 ['chave canônica de favoritos igual à chave do player',h.includes("const keyOf=x=>x&&x[4]!=null?'jm-'+String(x[4]):'';")],
 ['migração de favoritos antigos sem prefixo',h.includes("String(k).startsWith('jm-')?String(k):'jm-'+String(k)")],
 ['player e lista usam estado favorito sincronizado',h.includes('function syncFavoriteCatalog()')&&h.includes('rima-v29-player-heart')&&h.includes('[data-rima-fav]')],
 ['favoritos existentes mantêm chave de catálogo',h.includes("localStorage.setItem(KEY,JSON.stringify(fav))")],
 ['retomada de efeitos ao voltar para o app',h.includes("document.addEventListener('visibilitychange'")&&h.includes("window.addEventListener('pageshow'")],
 ['retomada do loop do palco e do player',h.includes('cancelAnimationFrame(zR)')&&h.includes('WD.raf=requestAnimationFrame(wLoop)')],
 ['retomada após rotação da tela',h.includes("window.addEventListener('orientationchange'")],
 ['palco separa palavra principal das sugestões',h.includes('min-height:clamp(76px,18vh,132px)!important')&&h.includes('margin:10px auto 9px!important')],
 ['player horizontal fixo abaixo do palco',h.includes('bottom:calc(58px + env(safe-area-inset-bottom,0px))!important')],
 ['versão 3.1.2 / code 54',g.includes('versionCode 54')&&g.includes("versionName '3.1.2'")]
];let bad=0;for(const [n,ok] of checks){console.log((ok?'PASS':'FAIL')+' '+n);if(!ok)bad++}if(bad)process.exit(1);
