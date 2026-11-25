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
/* Ajustes de UI, catálogo Jamendo e limites por categoria. */
const capAnchor = "Object.keys(ZLIB).forEach(st=>{const merged=[],seen=new Set();";
if (!html.includes(capAnchor)) throw new Error('Não encontrei o ponto de inicialização do catálogo Jamendo.');
if (!html.includes("const zCap=st=>st==='Boom bap'?40:50;")) {
  html = html.replace(capAnchor, "const zCap=st=>'Boom bap'?40:50;\n"+capAnchor);
}
const replacements = [
  ["merged.push(x);if(ZLEGACY[st]&&ZLEGACY[st].length)ZMIGRATED=true}}ZRAW[st]=merged.slice(0,50)});","merged.push(x);if(ZLEGACY[st]&&ZLEGACY[st].length)ZMIGRATED=true}}ZRAW[st]=merged.slice(0,zCap(st))});"],
  ["ZLIB[st][1]=L.slice(0,50)}","ZLIB[st][1]=L.slice(0,zCap(st))}"],
  ["if(picked.length>=50)break","if(picked.length>=zCap(st))break"],
  ["if(picked.length<50){for(const o of ranked)","if(picked.length<zCap(st)){for(const o of ranked)"],
  ["if(merged.length>=50)break","if(merged.length>=zCap(st))break"],
  ["if(ZSG[st]+1<ZQ[st].length&&good<50)","if(ZSG[st]+1<ZQ[st].length&&good<zCap(st))"],
  ["return rows>=50&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS","return rows>=zCap(st)&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS"],
  ["${ZLIB[s][1].length}/50","${ZLIB[s][1].length}/${zCap(s)}"]
];
for (const [a,b] of replacements) {
  if (html.includes(a)) html = html.split(a).join(b);
  else if (!html.includes(b)) throw new Error('Não encontrei trecho esperado: '+a.slice(0,90));
}
const qAnchor = "  ['search','boom bap underground beat'],['search','hip hop drums instrumental'],['search','90s rap instrumental'],\n  ['search','old school hip hop beat'],['search','breakbeat hip hop instrumental']";
const qAdd = qAnchor + ",\n" +
"  ['search','raw boom bap battle rap beat'],['search','underground freestyle cypher beat'],\n" +
"  ['search','dusty drums boom bap instrumental'],['search','hard east coast boom bap beat'],\n" +
"  ['search','jazzy boom bap freestyle instrumental'],['search','soul sample boom bap rap beat'],\n" +
"  ['search','grimy street hip hop instrumental'],['search','90s underground cypher beat'],\n" +
"  ['search','battle freestyle hip hop beat instrumental'],['search','boom bap drums vinyl sample'],\n" +
"  ['search','old school rap battle instrumental'],['search','brazilian underground rap instrumental'],\n" +
"  ['search','rap de batalha instrumental brasileiro'],['search','boom bap freestyle beat no vocals'],\n" +
"  ['search','hardcore east coast rap instrumental']";
if (!html.includes(qAnchor)) throw new Error('Não encontrei o fim da lista de buscas Boom bap.');
html = html.replace(qAnchor,qAdd);
const bpmOld = "const bd=Math.round(ZS.bpm*10)/10,tx=ZS.name+' - '+bd+' BPM'+(lk?' (fixo)':'');";
if (html.includes(bpmOld)) html = html.replace(bpmOld,"const bd=Math.round(ZS.bpm*10)/10,tx=ZS.name+' - '+bd+' BPM';");
else if (html.includes("(fixo)")) throw new Error('Ainda existe outro rótulo BPM fixo para revisar.');
const css = `
/* Rima Lab: refinamento de espaçamento e alinhamento da etapa 2 */
#bt > .mc + .mc{margin-top:14px!important}
#bt > .mc{margin-bottom:0!important}
#train-step-2 > .row:first-child .tag{flex:1;display:flex;align-items:center;justify-content:center;text-align:center;min-height:44px}
#train-step-2 > .row:first-child .bk{flex:1}
`;
if (!html.includes('Rima Lab: refinamento de espaçamento')) {
  const pos = html.lastIndexOf('</style>');
  if (pos < 0) throw new Error('Não encontrei o fechamento do CSS.');
  html = html.slice(0,pos)+css+html.slice(pos);
}
fs.writeFileSync(path, html, 'utf8');
console.log('Aplicado: Boom bap até 40, 15 buscas adicionais Jamendo, cartões de batalha espaçados, etapa 2 alinhada e BPM sem rótulo fixo.');
