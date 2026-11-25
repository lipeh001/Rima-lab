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
  ['etapa de treino continua com botão de voltar e parar', h.includes('onclick="lvStop()"')]
];
checks.push(
  ['Boom bap tem limite de 40 e outras categorias mantêm 50', h.includes("const zCap=st=>st==='Boom bap'?40:50") && h.includes("ZLIB[st][1]=L.slice(0,zCap(st))")],
  ['15 novas buscas específicas de boom bap foram adicionadas', h.includes("rap de batalha instrumental brasileiro") && h.includes("hardcore east coast rap instrumental")],
  ['catálogo consulta até completar o limite de cada estilo', h.includes("good<zCap(st)") && h.includes("rows>=zCap(st)")],
  ['rótulo BPM fixo foi removido', !h.includes("(fixo)")],
  ['cartões Contra o app e Com um amigo têm espaçamento', h.includes("#bt > .mc + .mc{margin-top:14px!important}")],
  ['indicador Etapa 2 fica centralizado', h.includes("#train-step-2 > .row:first-child .tag{flex:1;display:flex;align-items:center;justify-content:center;text-align:center;min-height:44px}")]
);
let bad=0; for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log(`${checks.length-bad}/${checks.length} verificações da tela de treino passaram`);
process.exit(bad?1:0);
