#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const clientId=process.env.JAMENDO_CLIENT_ID;
if(!clientId) throw new Error('JAMENDO_CLIENT_ID não configurado');
const searches=['boom bap','boom-bap','old school hip hop beat','underground hip hop instrumental','90s hip hop instrumental'];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function api(params){
  const p=new URLSearchParams({client_id:clientId,format:'json',limit:'200',include:'licenses,musicinfo',...params});
  const res=await fetch('https://api.jamendo.com/v3.0/tracks/?'+p,{headers:{accept:'application/json', 'user-agent':'RimaLab-license-audit/1.0'}});
  const body=await res.text(); if(!res.ok) throw new Error('HTTP '+res.status+' '+body.slice(0,200));
  const j=JSON.parse(body); if(j.headers?.status!=='success') throw new Error(JSON.stringify(j.headers));
  return j.results||[];
}
function isExactCommercialCCBY(t){
  const u=String(t.license_ccurl||'').toLowerCase().replace(/\\/g,'');
  return /creativecommons\\.org\\/licenses\\/by\\/(3\\.0|4\\.0)\\/?$/.test(u);
}
function styleScore(t){
 const s=[t.name,t.album_name,t.musicinfo?.tags?.genres?.join(' '),t.musicinfo?.tags?.instruments?.join(' ')].join(' ').toLowerCase();
 if(/lofi|lo-fi|ambient|chillout|sleep|relax|meditation|background/.test(s)) return -100;
 let n=0;
 if(/boom\\s?bap|boom-bap/.test(s)) n+=10;
 if(/old school|90s|underground|east coast|hardcore|hip hop|hip-hop/.test(s)) n+=3;
 if(/instrumental|beat/.test(s)) n+=2;
 if(/trap|phonk|drill/.test(s)) n-=5;
 return n;
}
(async()=>{
 const all=new Map();
 for(const term of searches){
  try{
   const rows=await api({search:term,vocalinstrumental:'instrumental',ccnc:'false',ccnd:'false',ccsa:'false',type:'single albumtrack'});
   for(const t of rows) if(isExactCommercialCCBY(t) && t.audiodownload_allowed===true && Number(t.duration)>=90 && styleScore(t)>=10) all.set(String(t.id),t);
   console.log('Consulta',term,'retornou',rows.length,'candidatos acumulados',all.size);
  }catch(e){console.log('ERRO consulta',term,String(e));}
  await sleep(300);
 }
 const tracks=[...all.values()].sort((a,b)=>styleScore(b)-styleScore(a)||Number(b.duration)-Number(a.duration)).slice(0,40).map(t=>({
  id:String(t.id),name:t.name,artist:t.artist_name,duration:t.duration,
  license:t.license_ccurl,download_allowed:t.audiodownload_allowed,
  url:'https://www.jamendo.com/track/'+t.id,
  score:styleScore(t)
 }));
 fs.mkdirSync('search-output',{recursive:true});
 fs.writeFileSync('search-output/jamendo-boombap-ccby.json',JSON.stringify({searches,found:tracks.length,tracks},null,2));
 const lines=['# Jamendo — busca Boom Bap CC BY','', 'Consultas: '+searches.join('; '),'Faixas aprovadas: '+tracks.length,'','| ID | Faixa | Artista | Duração | Licença | Download |','|---|---|---|---:|---|---|',
 ...tracks.map(t=>'| '+t.id+' | '+String(t.name).replace(/\\|/g,'/')+' | '+String(t.artist).replace(/\\|/g,'/')+' | '+t.duration+'s | CC BY | Sim |')];
 fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY,lines.join('\\n')+'\\n');
 console.log(JSON.stringify({found:tracks.length,tracks},null,2));
})().catch(e=>{console.error(e);process.exit(1);});
