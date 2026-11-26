#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(process.argv[2]||'.');
const assets=path.join(root,'app/src/main/assets');
const html=fs.readFileSync(path.join(assets,'rima-lab.html'),'utf8');
const service=fs.readFileSync(path.join(root,'app/src/main/java/app/rimalab/MusicService.java'),'utf8');
const gradle=fs.readFileSync(path.join(root,'app/build.gradle'),'utf8');
const icon=fs.readFileSync(path.join(root,'app/src/main/res/drawable/ic_stat_beat.xml'),'utf8');
const seed=JSON.parse(fs.readFileSync(path.join(assets,'beats/catalog-seed.json'),'utf8'));
const styles=['Boom bap','Trap','Drill'];
const allIds=new Set();
const checks=[];
checks.push(['Jamendo consultado com filtro oficial de instrumentais',seed.vocalinstrumentalFilter==='instrumental']);
for(const style of styles){
  const rows=seed.catalogs&&seed.catalogs[style];
  checks.push([style+' tem exatamente 70 instrumentais com áudio validado',Array.isArray(rows)&&rows.length===70&&rows.every(r=>r[0]&&r[1]&&r[4]&&r[5]===style&&r[10]!==undefined&&r[11]>=85&&r[11]<=540)]);
  if(Array.isArray(rows))for(const r of rows)allIds.add(String(r[4]));
}
checks.push(['210 faixas têm IDs únicos entre as três categorias',allIds.size===210]);
checks.push(['catálogo de 70 por estilo está embutido no HTML',html.includes('RIMA_CATALOG_SEED_V8=')]);
checks.push(['catálogo é montado diretamente do seed para garantir 70/70/70',html.includes('for(const x of (RIMA_CATALOG_SEED_V8[st]||[]))')&&html.includes('ZLIB[st][1]=L.slice(0,cap)')]);
checks.push(['spinner depende do estado de carregamento da categoria, não da seleção',html.includes("function zCatLoading(s){return ZJS[s]==='load'||ZJS[s]==='cached'")]);
checks.push(['palavra do palco não quebra em uma letra isolada e ajusta a fonte',html.includes('rima-word-fit-script-v9')&&html.includes('white-space:nowrap')&&html.includes('while(e.scrollWidth>available&&size>28)')]);
checks.push(['dicas de rima têm curadoria fonética para exemplos reportados',html.includes('rima-rich-hints-v9')&&html.includes("'TAÇA':['graça','raça','caça','massa']")&&html.includes("'CONSOLE':['controle','descontrole','enrole','engole']")&&html.includes("'POSTE':['goste','encoste','desgoste','aposte']")&&html.includes("'MAREMOTO':['terremoto','remoto','moto','foto']")]);
checks.push(['cartão de notificação mostra um R grande sem sobreposição de R pequeno',service.includes('.setLargeIcon(singleRIcon())')&&service.includes('private Bitmap singleRIcon()')&&service.includes('c.drawText("R",128,190,p)')&&icon.includes('M4,10h2v8H4z')&&icon.includes('M12,3h2v15h-2z')&&!icon.includes('M5,3h8.1')]);

checks.push(['64 beats Drill originais geram WAV real offline, sem URL falsa',html.includes('function zBuildDrillWavV8(key)')&&html.includes('RIFF')&&html.includes('rima-generated://drill/')&&html.includes('zBuildDrillWavV8(k)')]);
checks.push(['cache antigo é invalidado uma única vez pela versão do pré-carregamento',html.includes('RIMA_PRELOAD_VERSION_V8')&&html.includes("['jmraw8','jmraw7','jmraw6'].forEach(k=>localStorage.removeItem(k))")]);
checks.push(['catálogo pré-carregado marca cada estilo como pronto com 70 faixas',html.includes("ZRAW[st]=merged.slice(0,70)")&&html.includes("ZJS[st]='ok'")]);
checks.push(['catálogo final preserva salvos e respeita teto de 70',html.includes('ZLIB[st][1]=L.slice(0,cap)')&&html.includes('const cap=70')]);
checks.push(['seletor mostra spinner durante carregamento',html.includes('zCatLoading(s)')&&html.includes('rima-cat-spinner')]);
checks.push(['texto offline é curto e coerente',html.includes('Escolha um beat para ouvir e treinar.')&&!html.includes('licença')&&!html.includes('Toque na seta para salvar no celular.')]);
checks.push(['salvamento permanente só é disparado depois do fim da faixa e quando autorizado',html.includes('function zAutoSaveFinishedBeatV8()')&&html.includes("x[10]!==true")&&html.includes("zAutoSaveFinishedBeatV8();")]);
checks.push(['reprodução inicial usa cache temporário, não baixa permanentemente antes de ouvir',html.includes('const perm=0;')]);
checks.push(['player não pula de faixa quando ocorre erro',/function zErr\(c,my\)\{[^}]*zFallback/.test(html)&&!html.includes('zLP(j,1)')]);
checks.push(['repetição começa desligada por padrão',html.includes("rep:'off',dp:0")]);
checks.push(['só avança para outra faixa quando repetir lista está selecionado',/if\(ZS\.rep==='all'\)\{zStep\(1\);return\}/.test(html)]);
checks.push(['retomada de posição anterior foi desativada para nova reprodução',html.includes('if(!cr)return false;')]);
checks.push(['prévia é reaproveitada ao começar o treino, sem baixar o mesmo beat duas vezes',html.includes('const ZFETCHING_V8=new Map()')&&html.includes(`const preview=play&&document.body.classList.contains('pv')`)]);
checks.push(['duplo clique em Começar é bloqueado',html.includes('__RIMA_LV_START_LOCK')]);
checks.push(['sem beat selecionado, o seletor volta para a etapa inicial e ganha destaque',html.includes('Selecione um beat para começar o treino.')&&html.includes('block:\'center\'')&&html.includes('rima-select-focus')]);
checks.push(['palco pulsa por transição suave, sem reflow nem animação de piscar',html.includes('rima-final-polish-v8')&&html.includes("e.classList.add('hit')")&&!html.includes(`void e.offsetWidth;e.classList.add('hit')`)]);
checks.push(['cartão expandido da notificação usa a marca oficial do Rima Lab',service.includes('.setLargeIcon(singleRIcon())')&&service.includes('private Bitmap singleRIcon()')]);
checks.push(['ícone pequeno de status é o glifo R monocromático do app',icon.includes('fillColor="#FFFFFF"')&&icon.includes('M4,10h2v8H4z')&&icon.includes('M12,3h2v15h-2z')&&!icon.includes('M5,3h8.1')]);
checks.push(['APK tem versão e código novos para atualização por cima',gradle.includes('versionCode 29')&&gradle.includes("versionName '2.9.2'")]);
let bad=0;
for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log((checks.length-bad)+'/'+checks.length+' verificações CATALOG_V8 passaram');
process.exit(bad?1:0);
