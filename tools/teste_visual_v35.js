const fs=require('fs'),path=require('path'),root=path.resolve(process.argv[2]),h=fs.readFileSync(path.join(root,'app/src/main/assets/rima-lab.html'),'utf8'),g=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const checks=[
['view de favoritos não substitui o seletor de categorias',h.includes('function render()')&&h.includes('row.insertAdjacentElement')&&h.includes('list.hidden=favoritesMode')],
['botão favoritos alterna filtro sem substituir seletor',h.includes('function toggleView()')&&h.includes('window.rimaV29ShowFavorites=toggleView')],
['chave do beat igual à chave canônica jm-id',h.includes("const trackKey=x=>x&&x[4]!=null?'jm-'+String(x[4]):''")],
['coração do player usa a mesma ação persistente da lista',h.includes('p.onclick=function(e)')&&h.includes('window.rimaV29ToggleFav(k)')],
['estado visual sincronizado do coração',h.includes("setAttribute('aria-pressed',String(on))")],
['player horizontal movido para body e dock inferior',h.includes('document.body.appendChild(p)')&&h.includes("setProperty('bottom','calc(58px")],
['número correto no cabeçalho de escolha do modo',h.includes("if(n)n.textContent='1'")],
['versão 3.1.3 code 55',g.includes('versionCode 55')&&g.includes("versionName '3.1.3'")]
];let bad=0;for(const [n,ok] of checks){console.log((ok?'PASS':'FAIL')+' '+n);if(!ok)bad++}if(bad)process.exit(1);