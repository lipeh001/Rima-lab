#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path');
const assets=path.resolve(process.argv[2]||'app/src/main/assets');
const keyText=fs.readFileSync(path.join(assets,'jamendo.txt'),'utf8');
const m=keyText.match(/^\s*CLIENT_ID\s*=\s*(\S+)/m);
const clientId=m&&m[1];
if(!clientId||clientId.length<6||clientId.startsWith('COLE'))throw new Error('CLIENT_ID Jamendo inválido');

const queries=[
 ['fuzzytags','boombap+hiphop'],['fuzzytags','oldschool+hiphop'],['fuzzytags','underground+hiphop'],
 ['fuzzytags','jazzhop+hiphop'],['fuzzytags','hiphop+instrumental'],
 ['search','boom bap instrumental'],['search','boom bap beat'],['search','hip hop instrumental beat'],
 ['search','battle rap instrumental'],['search','freestyle rap beat instrumental'],['search','cypher hip hop instrumental'],
 ['search','east coast hip hop instrumental'],['search','rap nacional instrumental'],['search','brazilian boom bap instrumental'],
 ['search','batalha de rima instrumental'],['search','beat para batalha de rap'],['search','batalha da aldeia beat instrumental'],
 ['search','zona norte batalha de rima beat'],['search','boom bap brasileiro instrumental'],['search','rap paulista instrumental'],
 ['search','underground brazilian hip hop beat'],['search','gritty underground hip hop beat'],
 ['search','instrumental hip hop'],['search','hip hop instrumental'],['search','rap instrumental'],
 ['search','freestyle instrumental beat'],['search','old school rap instrumental'],['search','90s hip hop beat'],
 ['search','east coast rap beat'],['search','hardcore hip hop instrumental'],['search','underground rap instrumental'],
 ['search','cypher beat instrumental'],['search','boom bap type beat instrumental'],['search','jazz rap instrumental'],
 ['search','soul hip hop instrumental'],['search','gritty rap beat'],['search','street rap instrumental'],
 ['search','brazilian hip hop beat instrumental'],['search','instrumental rap beat'],['search','hiphop beat no vocals'],
 ['search','boom bap hip hop beat'],['search','classic hip hop instrumental'],['search','rap battle beat'],
 ['search','freestyle battle beat'],['search','hard boom bap instrumental'],['search','raw boom bap beat'],
 ['search','boom bap underground beat'],['search','hip hop drums instrumental'],['search','90s rap instrumental'],
 ['search','old school hip hop beat'],['search','breakbeat hip hop instrumental'],
 ['search','dark boom bap instrumental'],['search','boom bap 90 bpm instrumental'],['search','boom bap 95 bpm beat'],
 ['search','boom bap 100 bpm instrumental'],['search','raw underground boom bap instrumental'],['search','dusty vinyl boom bap beat'],
 ['search','jazzy boom bap instrumental'],['search','soulful boom bap beat'],['search','hardcore boom bap instrumental'],
 ['search','grimy east coast boom bap'],['search','boom bap drums and samples instrumental'],
 ['search','boom bap piano rap instrumental'],['search','boom bap guitar rap beat instrumental'],
 ['search','boom bap brass hip hop beat'],['search','boom bap loop instrumental hip hop'],
 ['search','old school battle rap beat'],['search','underground cypher boom bap beat'],
 ['search','instrumental rap boom bap 90s'],['search','hip hop sampler instrumental 90s'],
 ['search','classic east coast instrumental beat'],['search','boom bap freestyle instrumental no vocals'],
 ['search','boom bap battle instrumental no vocals'],['search','raw boom bap battle rap beat'],
 ['search','underground freestyle cypher beat'],['search','dusty drums boom bap instrumental'],
 ['search','hard east coast boom bap beat'],['search','jazzy boom bap freestyle instrumental'],
 ['search','soul sample boom bap rap beat'],['search','grimy street hip hop instrumental'],
 ['search','90s underground cypher beat'],['search','battle freestyle hip hop beat instrumental'],
 ['search','boom bap drums vinyl sample'],['search','old school rap battle instrumental'],
 ['search','brazilian underground rap instrumental'],['search','rap de batalha instrumental brasileiro'],
 ['search','boom bap freestyle beat no vocals'],['search','hardcore east coast rap instrumental']
];
const strong=/boom\s*[-]?\s*bap|boombap|old\s*[-]?\s*school|golden\s*era|east\s*coast|cypher|battle|batalha|freestyle|underground|90s|sampler|breakbeat|dusty|gritty/i;
const ban=/\btrap\b|\bdrill\b|house|techno|trance|dubstep|metal|rock|reggaeton|dancehall|country|vocal\s*[- ]?(male|female)|with\s+some\s+money|all\$?tarv/i;
function textOf(r){const t=r.musicinfo&&r.musicinfo.tags||{};return [r.name,r.album_name,r.artist_name,...(t.genres||[]),...(t.instruments||[]),...(t.vartags||[])].filter(Boolean).join(' ')}
function scoreOf(r){
 const vi=String(r.musicinfo&&r.musicinfo.vocalinstrumental||'').toLowerCase();
 if(vi&&vi!=='instrumental')return -1;
 const t=textOf(r);if(ban.test(t)||!strong.test(t))return -1;
 if(!/hip\s*[-]?\s*hop|hiphop|\brap\b|boombap|boom\s*[-]?\s*bap/i.test(t))return -1;
 let n=0;if(/boom\s*[-]?\s*bap|boombap/i.test(t))n+=12;
 if(/battle|batalha|freestyle|cypher/i.test(t))n+=8;
 if(/old\s*[-]?\s*school|90s|east\s*coast|golden\s*era/i.test(t))n+=6;
 if(/sampler|drums|percussion|breakbeat/i.test(t))n+=2;return n;
}
async function mapLimit(a,n,fn){const out=new Array(a.length);let next=0;await Promise.all(Array.from({length:Math.min(n,a.length)},async()=>{while(true){const i=next++;if(i>=a.length)return;try{out[i]=await fn(a[i],i)}catch(e){out[i]={__error:String(e)};console.error('QUERY_FAIL',a[i][0],a[i][1],String(e))}}}));return out}
async function fetchQuery(q){
 const base=[['client_id',clientId],['format','json'],['limit','200'],['include','musicinfo,licenses'],['imagesize','100'],['audioformat','mp32'],['audiodlformat','mp32'],['type','single albumtrack'],['vocalinstrumental','instrumental'],['order','relevance'],['boost','popularity_month']];
 let url='https://api.jamendo.com/v3.0/tracks/?'+base.map(([k,v])=>k+'='+encodeURIComponent(v)).join('&');
 url+='&'+q[0]+'='+(q[0]==='fuzzytags'?encodeURIComponent(q[1]).replace(/%2B/gi,'+'):encodeURIComponent(q[1]));
 const ctl=new AbortController(),timer=setTimeout(()=>ctl.abort(),20000);
 try{
  const res=await fetch(url,{signal:ctl.signal,headers:{'User-Agent':'RimaLab-Android/2.8','Accept':'application/json'}});
  const body=await res.text();if(!res.ok)throw new Error('HTTP '+res.status+' '+body.slice(0,200));
  const data=JSON.parse(body);
  if(data.headers&&data.headers.status&&data.headers.status!=='success')throw new Error('Jamendo '+JSON.stringify(data.headers));
  const rows=Array.isArray(data.results)?data.results:[];
  console.log('QUERY_OK',q[0]+'='+q[1],'rows='+rows.length,'sample='+(rows[0]?String(rows[0].name)+' / '+String(rows[0].musicinfo&&rows[0].musicinfo.vocalinstrumental):'none'));
  return rows;
 }finally{clearTimeout(timer)}
}
async function probeAudio(url){
 const ctl=new AbortController(),timer=setTimeout(()=>ctl.abort(),10000);
 try{
  const res=await fetch(url,{headers:{Range:'bytes=0-2047',Accept:'audio/mpeg,audio/*;q=0.9,*/*;q=0.1'},signal:ctl.signal});
  const ct=String(res.headers.get('content-type')||'').toLowerCase();
  if(!res.ok||(ct&&!/(audio|mpeg|octet-stream)/.test(ct))){try{await res.body?.cancel()}catch(_){}return false}
  const reader=res.body&&res.body.getReader?res.body.getReader():null;if(!reader)return false;
  const first=await reader.read();try{await reader.cancel()}catch(_){}return !!(first&&first.value&&first.value.byteLength>=256);
 }catch(_){return false}finally{clearTimeout(timer)}
}
(async()=>{
 console.log('Jamendo client_id lido:',clientId.slice(0,3)+'…'+clientId.slice(-2));
 console.log('Consultando Jamendo:',queries.length,'pesquisas de Boom bap');
 const batches=await mapLimit(queries,4,async q=>{
  const rows=await fetchQuery(q);
  const viable=rows.filter(r=>r&&r.id&&r.audio&&Number(r.duration)>=85&&Number(r.duration)<=540&&scoreOf(r)>=0);
  console.log('ELIGIBLE',q[0]+'='+q[1],viable.length);
  return viable;
 });
 const byId=new Map();
 for(const batch of batches)for(const r of (batch||[])){
  if(r.__error)continue;const id=String(r.id);const prev=byId.get(id);
  if(!prev||scoreOf(r)>scoreOf(prev))byId.set(id,r);
 }
 const ranked=[...byId.values()].sort((a,b)=>scoreOf(b)-scoreOf(a)||String(a.name).localeCompare(String(b.name)));
 console.log('Candidatos instrumentais compatíveis:',ranked.length);
 if(!ranked.length)throw new Error('Jamendo não devolveu nenhuma faixa elegível. Não vou inventar catálogo.');
 const uniq=[],rest=[],seenArtist=new Set();
 for(const r of ranked){const a=String(r.artist_id||r.artist_name||'').toLowerCase();if(!seenArtist.has(a)){seenArtist.add(a);uniq.push(r)}else rest.push(r)}
 const probed=await mapLimit(uniq.concat(rest),6,async r=>({r,ok:await probeAudio(r.audio)}));
 const tracks=[];
 for(const p of probed){if(!p||!p.ok||tracks.length>=30)continue;const r=p.r;
  tracks.push({id:String(r.id),name:String(r.name||'Boom bap instrumental').replace(/\s+/g,' ').trim(),artist:String(r.artist_name||'Artista independente'),duration:Number(r.duration)||0,audio:String(r.audio),shareurl:String(r.shareurl||('https://www.jamendo.com/track/'+r.id)),license:Array.isArray(r.licenses)&&r.licenses.length?String(r.licenses[0].shortname||r.licenses[0].name||'Ver licença'):'Ver licença na Jamendo',audiodownload:String(r.audiodownload||''),audiodownload_allowed:r.audiodownload_allowed===true&&!!r.audiodownload,bpm:0});
  console.log('AUDIO_OK',tracks.length+'/30',tracks[tracks.length-1].name);
 }
 if(!tracks.length)throw new Error('Jamendo encontrou faixas, mas nenhum stream passou no teste de áudio.');
 const dir=path.join(assets,'beats');fs.mkdirSync(dir,{recursive:true});
 fs.writeFileSync(path.join(dir,'boom-bap-extra.json'),JSON.stringify({version:'2026-11-25-boom-bap-verified',source:'Jamendo API v3.0',count:tracks.length,target:30,generatedAt:new Date().toISOString(),tracks},null,2),'utf8');
 console.log('CATALOG_OK:',tracks.length,'faixas instrumentais com stream acessível.');
})().catch(e=>{console.error(e);process.exit(1)});
