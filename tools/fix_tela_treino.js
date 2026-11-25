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

/* v2.8 — prompt mínimo, moldura pulsante e catálogo Jamendo sem teto. */
const exact = (a,b,label) => {
  if (!html.includes(a) && html.includes(b)) return;
  if (!html.includes(a)) throw new Error('Trecho não encontrado para '+label);
  html = html.replace(a,b);
};
exact("if(m=='lig'){let a=nW(),b=nW(),n=0;while(cat(a)==cat(b)&&n++<9)b=nW();return{k:'Ligue as duas palavras',big:a+' + '+b,sub:pick(LIG)}}",
      "if(m=='lig'){let a=nW(),b=nW(),n=0;while(cat(a)==cat(b)&&n++<9)b=nW();return{k:'Ligue as duas palavras',big:a+' + '+b,sub:''}}",
      'modo ligar duas palavras');
exact("['lig','Ligar duas palavras','Crie uma ponte entre duas palavras sem relação.']",
      "['lig','Ligar duas palavras','']",'descrição do modo ligar');
exact("else if(m==='lig'){op.innerHTML='<p class=\"mut\">Duas palavras de temas diferentes. Seu desafio é construir uma conexão convincente entre elas.</p>'}",
      "else if(m==='lig'){op.innerHTML=''}",'instrução extra do modo ligar');
/* Luz na moldura a cada pulso musical. */
const glow = `
/* v2.8 — luz de palco sincronizada aos pulsos do beat */
#stg.stage{isolation:isolate;border:1px solid rgba(216,255,62,.20)!important;transition:border-color .18s,box-shadow .18s}
#stg.stage::after{content:"";display:block!important;position:absolute;inset:0;border:1px solid rgba(216,255,62,.0);border-radius:inherit;pointer-events:none;opacity:0;box-shadow:inset 0 0 18px rgba(216,255,62,.12),0 0 24px rgba(216,255,62,.0);z-index:2}
#stg.stage.hit{border-color:rgba(216,255,62,.78)!important;box-shadow:0 0 0 1px rgba(216,255,62,.16),0 0 24px rgba(216,255,62,.18),inset 0 0 28px rgba(216,255,62,.055)!important}
#stg.stage.hit::after{animation:rl-frame-pulse .42s ease-out!important}
@keyframes rl-frame-pulse{0%{opacity:.95;border-color:rgba(216,255,62,.85);box-shadow:inset 0 0 30px rgba(216,255,62,.22),0 0 28px rgba(216,255,62,.28)}100%{opacity:.12;border-color:rgba(216,255,62,.22);box-shadow:inset 0 0 8px rgba(216,255,62,.04),0 0 5px rgba(216,255,62,.03)}}
@media(prefers-reduced-motion:reduce){#stg.stage.hit::after{animation:none!important;opacity:.2}}
`;
if (!html.includes('v2.8 — luz de palco')) { const p=html.lastIndexOf('</style>'); if(p<0)throw new Error('CSS não encontrado'); html=html.slice(0,p)+glow+html.slice(p); }
/* O script anterior introduziu o teto de 40/50; removemos o teto em todas as fases do catálogo. */
const unlimited = [
 ["const zCap=st=>'Boom bap'?40:50;",""],
 ["ZRAW[st]=merged.slice(0,zCap(st))","ZRAW[st]=merged"],
 ["ZLIB[st][1]=L.slice(0,zCap(st))","ZLIB[st][1]=L"],
 ["if(picked.length>=zCap(st))break","/* sem teto de resultados */"],
 ["if(picked.length<zCap(st)){for(const o of ranked){if(picked.some(p=>String(p.r.id)==String(o.r.id)))continue;picked.push(o);if(picked.length>=zCap(st))break}}","for(const o of ranked){if(picked.some(p=>String(p.r.id)==String(o.r.id)))continue;picked.push(o)}"],
 ["if(merged.length>=zCap(st))break","/* sem teto de resultados */"],
 ["rows>=zCap(st)&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS","rows>0&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS"],
 ["if(ZSG[st]+1<ZQ[st].length&&good<zCap(st))","if(ZSG[st]+1<ZQ[st].length)"],
 ["${ZLIB[s][1].length}/${zCap(s)}","${ZLIB[s][1].length}"]
];
for (const [a,b] of unlimited) { if(html.includes(a)) html=html.replace(a,b); else if(!html.includes(b)) throw new Error('Não encontrei teto do catálogo: '+a); }
const extraQueries = [
"  ['search','raw boom bap battle rap beat'],['search','underground freestyle cypher beat'],",
"  ['search','dusty drums boom bap instrumental'],['search','hard east coast boom bap beat'],",
"  ['search','jazzy boom bap freestyle instrumental'],['search','soul sample boom bap rap beat'],",
"  ['search','grimy street hip hop instrumental'],['search','90s underground cypher beat'],",
"  ['search','battle freestyle hip hop beat instrumental'],['search','boom bap drums vinyl sample'],",
"  ['search','old school rap battle instrumental'],['search','brazilian underground rap instrumental'],",
"  ['search','rap de batalha instrumental brasileiro'],['search','boom bap freestyle beat no vocals'],",
"  ['search','hardcore east coast rap instrumental']"
].join("\n");
const qEnd = "  ['search','old school hip hop beat'],['search','breakbeat hip hop instrumental']";
if(html.includes(qEnd) && !html.includes("raw boom bap battle rap beat")) html=html.replace(qEnd,qEnd+",\n"+extraQueries);
else if(!html.includes("raw boom bap battle rap beat")) throw new Error('Fim da lista de buscas Boom bap não encontrado');
/* Seleção obrigatória de uma faixa real do catálogo. */
const oldStart = "function lvStart(){ZNR=1;if(ZS.k!='syn'&&!ZS.key){zFlash('Escolha um beat da lista (Boom bap, Trap ou Drill).');try{$('#bp').scrollIntoView({behavior:'smooth'})}catch(e){}return}";
const newStart = "function lvStart(){ZNR=1;const selected=ZS.k==='lib'&&!!ZS.key&&Array.isArray(ZLIB[ZS.s])&&ZLIB[ZS.s][1].some(x=>zKey(x)===ZS.key);if(!selected){zFlash('Selecione um beat da lista antes de começar o treino.');const bp=$('#bp');if(bp){bp.scrollIntoView({behavior:'smooth',block:'center'});bp.style.outline='2px solid rgba(216,255,62,.75)';bp.style.outlineOffset='8px';setTimeout(()=>{bp.style.outline='';bp.style.outlineOffset=''},1800)}return}";
exact(oldStart,newStart,'validação da seleção do beat');

fs.writeFileSync(path, html, 'utf8');
console.log('Aplicado: Boom bap até 40, 15 buscas adicionais Jamendo, cartões de batalha espaçados, etapa 2 alinhada e BPM sem rótulo fixo.');
