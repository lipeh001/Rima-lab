const fs = require('fs');
const p = process.argv[2] || 'app/src/main/assets/rima-lab.html';
const h = fs.readFileSync(p, 'utf8');
const lv = h.indexOf('<div id="lv" hidden>');
const stage = h.indexOf('<div class="card stage" id="stg"', lv);
const checks = [
  ['lvStart não oculta o contêiner #su que contém a tela #lv', !h.includes("$('#su').hidden=true")],
  ['tela de treino contém o palco depois do início da tela', lv >= 0 && stage > lv],
  ['calibração antiga é zerada uma única vez após atualização', h.includes("rimalab_lat_reset_v1") && h.includes("localStorage.removeItem('lat')")],
  ['calibração manual continua salvando o ajuste escolhido', h.includes("function setLat(v){LAT=v;LATSET=true;try{localStorage.setItem('lat',v)")],
  ['etapa de treino continua com botão de voltar e parar', h.includes('onclick="lvStop()"')],
  ['modo Ligar duas palavras mostra somente o par, sem instrução', h.includes("big:a+' + '+b,sub:''") && h.includes("else if(m==='lig'){op.innerHTML=''}")],
  ['moldura do palco tem pulso luminoso sincronizado', h.includes('v2.8 — luz de palco') && h.includes('rl-frame-pulse') && h.includes('#stg.stage.hit::after')],
  ['catálogo pré-carrega 70 faixas em cada estilo e limita listas a 70', h.includes('RIMA_CATALOG_SEED_V8=') && h.includes('const cap=70') && h.includes('ZLIB[st][1]=L.slice(0,cap)') && h.includes('ZRAW[st]=merged.slice(0,70)')],
  ['15 novas buscas de boom bap voltadas a batalha foram adicionadas', h.includes('rap de batalha instrumental brasileiro') && h.includes('hardcore east coast rap instrumental')],
  ['Jamendo percorre todas as buscas da categoria', h.includes('ZSG[st]+1<ZQ[st].length)')],
  ['início exige seleção de um beat e mostra aviso', h.includes('Selecione um beat da lista antes de começar o treino.') && h.includes("ZS.k==='lib'")]
];
let bad=0;
for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log(`${checks.length-bad}/${checks.length} verificações da tela de treino passaram`);
process.exit(bad?1:0);
