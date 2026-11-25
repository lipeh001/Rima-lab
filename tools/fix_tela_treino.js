/* Corrige a tela de treino e limpa uma calibragem antiga herdada sem consentimento explícito. */
const fs = require('fs');
const path = process.argv[2] || 'app/src/main/assets/rima-lab.html';
let html = fs.readFileSync(path, 'utf8');
const oldLat = 'let LAT=0;try{LAT=+localStorage.getItem("lat")||0}catch(e){}';
const newLat = "let LAT=0;try{if(localStorage.getItem('rimalab_lat_reset_v1')!=='1'){localStorage.removeItem('lat');localStorage.setItem('rimalab_lat_reset_v1','1')}LAT=+localStorage.getItem('lat')||0}catch(e){}";
if (html.includes(oldLat)) html = html.replace(oldLat, newLat);
else if (!html.includes("rimalab_lat_reset_v1")) throw new Error('Não encontrei a inicialização da calibração esperada.');
const oldHide = "$('#su').hidden=true;const screen=$('#lv');";
if (html.includes(oldHide)) html = html.replace(oldHide, "const screen=$('#lv');");
else if (html.includes("$('#su').hidden=true")) throw new Error('Há outra ocultação do contêiner pai da tela de treino; revisar antes de compilar.');
if (html.includes("$('#su').hidden=true")) throw new Error('A tela de treino ainda oculta seu contêiner pai.');
fs.writeFileSync(path, html, 'utf8');
console.log('Correção aplicada: tela de treino permanece visível e calibragem antiga é zerada uma única vez.');
