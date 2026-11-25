#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const assets = path.resolve(process.argv[2] || 'app/src/main/assets');
const jamendoKeyPath = path.join(assets, 'jamendo.txt');
if (!fs.existsSync(jamendoKeyPath)) throw new Error('jamendo.txt não encontrado nos assets.');
const keyMatch = fs.readFileSync(jamendoKeyPath, 'utf8').match(/^\s*CLIENT_ID\s*=\s*(\S+)/m);
const clientId = keyMatch && keyMatch[1];
if (!clientId || clientId.length < 6 || clientId.startsWith('COLE')) throw new Error('CLIENT_ID do Jamendo ausente ou inválido.');

const queries = [
  ['search','boom bap instrumental'],
  ['search','boom bap beat'],
  ['search','raw boom bap instrumental'],
  ['search','boom bap battle rap beat'],
  ['search','boom bap freestyle instrumental'],
  ['search','boom bap cypher instrumental'],
  ['search','old school hip hop instrumental'],
  ['search','90s hip hop instrumental'],
  ['search','east coast hip hop instrumental'],
  ['search','underground hip hop instrumental'],
  ['search','underground cypher beat'],
  ['search','battle rap instrumental beat'],
  ['search','freestyle rap instrumental'],
  ['search','batalha de rima instrumental'],
  ['search','rap de batalha instrumental'],
  ['search','brazilian boom bap instrumental'],
  ['search','golden era hip hop beat'],
  ['search','dusty drums hip hop instrumental'],
  ['search','jazzy boom bap instrumental'],
  ['search','soulful boom bap beat'],
  ['search','gritty boom bap instrumental'],
  ['search','dark boom bap instrumental'],
  ['search','hardcore boom bap instrumental'],
  ['search','boom bap sampler instrumental'],
  ['search','boom bap breakbeat instrumental'],
  ['search','boom bap 90 bpm'],
  ['search','boom bap 95 bpm'],
  ['search','boom bap 100 bpm'],
  ['search','old school rap battle beat'],
  ['search','hip hop cypher instrumental'],
  ['search','freestyle battle beat instrumental'],
  ['search','hip hop beat no vocals 90s'],
  ['search','rap instrumental 90s sampler'],
  ['search','Funky Old-School Hip-Hop Style Instrumental Cypher House'],
  ['search','DARK BOOM BAP 08'],
  ['search','90s BOOM BAP 227'],
  ['search','Boom Bap Old School Hip Hop AVANT-BEATS'],
  ['search','Hip-Hop Boom Bap Royalty Free Music'],
  ['search','El Emperador Del Rap FreeStyle Vol 1']
];

const strong = /boom\s*[-]?\s*bap|boombap|old\s*[-]?\s*school|golden\s*era|east\s*coast|cypher|battle|batalha|freestyle|underground|90s|sampler|breakbeat|dusty|gritty/i;
const ban = /trap|drill|house|techno|trance|dubstep|metal|rock|reggaeton|dancehall|country|vocal\s*[- ]?(male|female)|with\s+some\s+money|all\$?tarv/i;

function textOf(r) {
  const tags = (r.musicinfo && r.musicinfo.tags) || {};
  return [r.name, r.album_name, ...(tags.genres || []), ...(tags.instruments || []), ...(tags.vartags || []), ...(tags.moods || [])].filter(Boolean).join(' ');
}
function scoreOf(r) {
  const info = r.musicinfo || {};
  if (String(info.vocalinstrumental || '').toLowerCase() !== 'instrumental') return -1;
  const text = textOf(r);
  if (ban.test(text) || !strong.test(text)) return -1;
  const genres = ((info.tags || {}).genres || []).join(' ');
  if (!/hip\s*[-]?\s*hop|hiphop|rap/i.test(genres + ' ' + text)) return -1;
  let score = 0;
  if (/boom\s*[-]?\s*bap|boombap/i.test(text)) score += 12;
  if (/battle|batalha|freestyle|cypher/i.test(text)) score += 8;
  if (/old\s*[-]?\s*school|90s|east\s*coast|golden\s*era/i.test(text)) score += 6;
  if (/sampler|drums|percussion|breakbeat/i.test(text)) score += 2;
  if (/underground|gritty|dusty|urban/i.test(text)) score += 1;
  return score;
}

async function mapLimit(items, limit, fn) {
  const out = new Array(items.length); let next = 0;
  const workers = Array.from({length: Math.min(limit, items.length)}, async () => {
    while (true) { const i = next++; if (i >= items.length) return; try { out[i] = await fn(items[i], i); } catch (e) { out[i] = null; } }
  });
  await Promise.all(workers); return out;
}

async function fetchQuery(q) {
  const params = new URLSearchParams({
    client_id: clientId, format: 'json', limit: '200',
    include: 'musicinfo,licenses', imagesize: '100',
    audioformat: 'mp32', audiodlformat: 'mp32',
    type: 'single albumtrack', vocalinstrumental: 'instrumental',
    durationbetween: '85_540', order: 'relevance', boost: 'popularity_month'
  });
  params.set(q[0], q[1]);
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 18000);
  try {
    const res = await fetch('https://api.jamendo.com/v3.0/tracks/?' + params.toString(), {
      signal: ctl.signal, headers: {'User-Agent':'RimaLab-Android/2.8','Accept':'application/json'}
    });
    if (!res.ok) throw new Error('Jamendo HTTP ' + res.status);
    const data = await res.json();
    return Array.isArray(data.results) ? data.results : [];
  } finally { clearTimeout(timer); }
}

async function probeAudio(url) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 9000);
  try {
    const res = await fetch(url, {
      method: 'GET',
      headers: {'Range':'bytes=0-2047','Accept':'audio/mpeg,audio/*;q=0.9,*/*;q=0.1','User-Agent':'RimaLab-Android/2.8'},
      signal: ctl.signal
    });
    const ct = String(res.headers.get('content-type') || '').toLowerCase();
    if (!res.ok || (ct && !/(audio|mpeg|octet-stream)/.test(ct))) {
      try { await res.body?.cancel(); } catch (_) {}
      return false;
    }
    const reader = res.body && res.body.getReader ? res.body.getReader() : null;
    if (!reader) return false;
    const first = await reader.read();
    try { await reader.cancel(); } catch (_) {}
    return !!(first && first.value && first.value.byteLength >= 256);
  } catch (_) { return false; }
  finally { clearTimeout(timer); }
}

(async () => {
  console.log('Consultando Jamendo: ' + queries.length + ' pesquisas instrumentais de Boom bap...');
  const batches = await mapLimit(queries, 4, async q => {
    const rows = await fetchQuery(q);
    return rows.map(r => ({r, score: scoreOf(r)})).filter(x => x.score >= 0);
  });
  const byId = new Map();
  for (const batch of batches) for (const item of (batch || [])) {
    const id = String(item.r.id || '');
    if (!id || !item.r.audio) continue;
    const prev = byId.get(id);
    if (!prev || item.score > prev.score) byId.set(id, item);
  }
  const ranked = [...byId.values()].sort((a,b) => b.score-a.score || String(a.r.name).localeCompare(String(b.r.name)));
  console.log('Candidatos instrumentais e compatíveis: ' + ranked.length);

  // Prioriza variedade: primeiro um beat por artista, depois completa se o catálogo exigir.
  const uniqueArtists = [], artistSet = new Set(), rest = [];
  for (const item of ranked) {
    const artist = String(item.r.artist_id || item.r.artist_name || '').toLowerCase();
    if (!artistSet.has(artist)) { artistSet.add(artist); uniqueArtists.push(item); }
    else rest.push(item);
  }
  const ordered = uniqueArtists.concat(rest);
  const verified = [];
  for (const item of ordered) {
    if (verified.length >= 30) break;
    const r = item.r;
    if (!(await probeAudio(r.audio))) continue;
    const lic = Array.isArray(r.licenses) && r.licenses.length
      ? String(r.licenses[0].shortname || r.licenses[0].name || 'Ver licença')
      : 'Ver licença na Jamendo';
    verified.push({
      id: String(r.id),
      name: String(r.name || 'Boom bap instrumental').replace(/\s+/g,' ').trim(),
      artist: String(r.artist_name || 'Artista independente'),
      duration: Number(r.duration) || 0,
      audio: String(r.audio),
      shareurl: String(r.shareurl || ('https://www.jamendo.com/track/' + r.id)),
      license: lic,
      audiodownload: String(r.audiodownload || ''),
      audiodownload_allowed: r.audiodownload_allowed === true && !!r.audiodownload,
      bpm: 0
    });
    console.log('VALIDADO ' + verified.length + '/30: ' + verified[verified.length-1].name + ' — ' + verified[verified.length-1].artist);
  }
  if (verified.length < 30) {
    console.error('Jamendo retornou apenas ' + verified.length + ' faixas compatíveis com os filtros e com áudio acessível; não vou inventar beats para completar 30.');
    process.exit(2);
  }
  const dir = path.join(assets, 'beats');
  fs.mkdirSync(dir, {recursive:true});
  const out = path.join(dir, 'boom-bap-extra.json');
  fs.writeFileSync(out, JSON.stringify({
    version: '2026-11-25-bb30-v1',
    source: 'Jamendo API v3.0',
    verifiedCount: verified.length,
    generatedAt: new Date().toISOString(),
    tracks: verified
  }, null, 2), 'utf8');
  console.log('Catálogo salvo: ' + out + ' (' + verified.length + ' faixas com áudio validado).');
})().catch(err => { console.error(err); process.exit(1); });
