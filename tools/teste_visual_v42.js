#!/usr/bin/env node
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]);
const h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8');
const gp=['app/build.gradle','app/build.gradle.kts'].map(p=>path.join(root,p)).find(fs.existsSync);
if(!gp)throw new Error('Gradle file missing');
const g=fs.readFileSync(gp,'utf8');
const script=h.match(/<script id="rimalab-selector-favorites-sync-v42">([\s\S]*?)<\/script>/)?.[1]||'';
const css=h.match(/<style id="rimalab-landscape-player-dock-v42">([\s\S]*?)<\/style>/)?.[1]||'';
const checks=[
 ['runtime V42 posterior ao player/playlist V41',h.indexOf('rimalab-playlist-player-landscape-v41')>=0&&h.indexOf('rimalab-selector-favorites-sync-v42')>h.indexOf('rimalab-playlist-player-landscape-v41')],
 ['controlador compartilha #bp e #bq',script.includes("['bp','bq']")&&script.includes('#bp .rima-v42-favorites-toggle,#bq .rima-v42-favorites-toggle')],
 ['Favoritos clicável na etapa 2/2 e no treino',script.includes('#bp .rima-v42-favorites-toggle')&&script.includes('#bq .rima-v42-favorites-toggle')],
 ['seleção de categorias removida ao entrar em Favoritos',script.includes("b.classList.remove('on')")&&script.includes("setMode(!favoritesMode")],
 ['aba Favoritos destacada e com contagem',script.includes("b.classList.toggle('active',favoritesMode)")&&script.includes('rima-v29-count')],
 ['lista de favoritos montada a partir dos itens salvos',script.includes('tracks().filter(t=>saved.includes(t.key))')],
 ['título de cada favorito é ação de reprodução',script.includes('data-rima-v42-play')&&script.includes('playFavorite(key)')],
 ['tocar favorito inicia fila exclusiva V41',script.includes('window.rimaV41StartFavorites(key)')],
 ['coração remove favorito usando persistência existente',script.includes('data-rima-v42-heart')&&script.includes('window.rimaV29ToggleFav(k)')],
 ['selecionar categoria fecha Favoritos em ambos',script.includes('#bp .row .tag.chip,#bq .row .tag.chip')&&script.includes('closeForCategory()')],
 ['render após reconstrução pk preserva Favoritos',script.includes('const oldPk=window.pk')&&script.includes('renderAll()')],
 ['shuffle/repeat V41 continuam no player',h.includes('window.zShuf=function()')&&h.includes('window.zRep=function()')],
 ['estilo visual compartilhado pelos dois seletores',css.includes('#bp .rima-v29-tools,#bq .rima-v29-tools')&&css.includes('#bp .rima-v42-favlist,#bq .rima-v42-favlist')],
 ['player horizontal fixado no rodapé',css.includes('inset:auto 8px 5px 8px!important')&&script.includes("set('bottom','5px')")],
 ['player não ignora visibilidade sob demanda',script.includes('rima-player-visible')&&!script.includes("set('display',document.body.classList.contains('pl')")],
 ['controles −10s/+10s visíveis',css.includes('.pwscr .pwm')&&css.includes('display:grid!important')],
 ['seek bar visível e clicável',css.includes('.pwscr .pwp')&&css.includes('display:block!important')],
 ['player compacto 70px',css.includes('height:70px!important')&&css.includes('max-height:70px!important')],
 ['palco horizontal compacto sem esticar',css.includes('height:clamp(245px,calc(100svh - 200px),295px)')&&css.includes('max-height:295px!important')],
 ['seletor direito com rolagem interna e margem enxuta',css.includes('overflow-y:auto!important')&&css.includes('margin:0!important;padding:7px 8px!important')],
 ['tratamento para paisagem curta',css.includes('max-height:380px')&&script.includes('orientationchange')],
 ['versão 3.2.0 / código 62',/versionCode\s*=\s*62|versionCode\s+62/.test(g)&&/versionName\s*=\s*['"]3\.2\.0['"]|versionName\s+['"]3\.2\.0['"]/.test(g)]
];
let bad=0;for(const [name,ok] of checks){console.log((ok?'PASS ':'FAIL ')+name);if(!ok)bad++}
if(bad)process.exit(1);
console.log(checks.length+'/'+checks.length+' verificações V42 passaram');
