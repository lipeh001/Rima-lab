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
let bad=0; for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log(`${checks.length-bad}/${checks.length} verificações da tela de treino passaram`);
process.exit(bad?1:0);
