const fs = require('fs');
const p = process.argv[2] || 'app/src/main/assets/rima-lab.html';
const h = fs.readFileSync(p, 'utf8');
const checks = [
  ['lvStart não oculta o contêiner #su que contém a tela #lv', !h.includes("$('#su').hidden=true")],
  ['tela de treino tem palco visível no HTML', /<div id="lv" hidden>[\\s\\S]*?<div class="card stage" id="stg"/.test(h)],
  ['calibração antiga é zerada uma única vez após atualização', h.includes("rimalab_lat_reset_v1") && h.includes("localStorage.removeItem('lat')")],
  ['calibração manual continua salvando o ajuste escolhido', /function setLat\\(v\\)\\{LAT=v;LATSET=true;try\\{localStorage\\.setItem\\('lat',v\\)/.test(h)],
  ['etapa de treino continua com botão de voltar e parar', h.includes('onclick="lvStop()"')]
];
let bad=0; for(const [name,ok] of checks){console.log((ok?'OK  ':'FAIL ')+name);if(!ok)bad++;}
console.log(`${checks.length-bad}/${checks.length} verificações da tela de treino passaram`);
process.exit(bad?1:0);
