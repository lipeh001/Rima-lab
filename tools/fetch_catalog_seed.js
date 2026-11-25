#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const assets = path.resolve(process.argv[2] || 'app/src/main/assets');
const keyText = fs.readFileSync(path.join(assets, 'jamendo.txt'), 'utf8');
const m = keyText.match(/^\s*CLIENT_ID\s*=\s*(\S+)/m);
const clientId = m && m[1];
if (!clientId || clientId.length < 6 || clientId.startsWith('COLE')) {
  throw new Error('CLIENT_ID Jamendo inválido');
}

const TARGET = 70;
const CONFIG = {
  'Boom bap': {
    queries: [
      ['fuzzytags','boombap+hiphop'],
      ['fuzzytags','oldschool+hiphop'],
      ['search','boom bap instrumental'],
      ['search','boom bap drums vinyl sample'],
      ['search','dusty drums boom bap instrumental'],
      ['search','grimy east coast boom bap']
    ],
    strong: /boom\s*[-]?\s*bap|boombap|old\s*[-]?\s*school|golden\s*era|east\s*coast|cypher|battle|batalha|freestyle|underground|90s|sampler|breakbeat|dusty|gritty/i,
    ban: /\btrap\b|\bdrill\b|house|techno|trance|dubstep|metal|rock|reggaeton|dancehall|country|lo[\s-]?fi|chill|relax|ambient|christmas|holiday|summer|good\s*vibes/i,
    minScore: 5
  },
  'Trap': {
    queries: [
      ['fuzzytags','trap+hiphop'],
      ['fuzzytags','trap+instrumental'],
      ['search','trap beat instrumental'],
      ['search','dark trap instrumental'],
      ['search','808 trap beat instrumental'],
      ['search','melodic trap instrumental']
    ],
    strong: /\btrap\b|808|dark\s*trap|melodic\s*trap|trap\s*beat/i,
    ban: /boom\s*[-]?\s*bap|boombap|\bdrill\b|house|techno|trance|dubstep|metal|rock|reggaeton|dancehall|lo[\s-]?fi|chill|relax|ambient|christmas|holiday/i,
    minScore: 4
  },
  'Drill': {
    queries: [
      ['fuzzytags','drill+hiphop'],
      ['fuzzytags','drill+instrumental'],
      ['search','drill beat instrumental'],
      ['search','uk drill instrumental'],
      ['search','dark drill beat instrumental'],
      ['search','ny drill instrumental beat']
    ],
    strong: /\bdrill\b|uk\s*drill|ny\s*drill|dark\s*drill|drill\s*beat/i,
    ban: /boom\s*[-]?\s*bap|boombap|\btrap\b|house|techno|trance|dubstep|metal|rock|reggaeton|dancehall|lo[\s-]?fi|chill|relax|ambient|christmas|holiday/i,
    minScore: 4
  }
};

const textOf = r => {
  const mi = r && r.musicinfo || {};
  const tags = mi.tags || {};
  return [r && r.name, r && r.album_name, r && r.artist_name]
    .concat(tags.genres || [], tags.vartags || [], tags.instruments || [], tags.moods || [])
    .filter(Boolean).join(' ');
};
function scoreOf(style, r) {
  const mi = r && r.musicinfo || {};
  const vocal = String(mi.vocalinstrumental || '').trim().toLowerCase();
  if (vocal && vocal !== 'instrumental') return -1;
  const t = textOf(r), c = CONFIG[style];
  if (c.ban.test(t) || !c.strong.test(t)) return -1;
  if (!/hip\s*[-]?\s*hop|hiphop|\brap\b|beat|instrumental/i.test(t)) return -1;
  let n = 0;
  if (style === 'Boom bap' && /boom\s*[-]?\s*bap|boombap/i.test(t)) n += 12;
  if (style === 'Trap' && /\btrap\b|808/i.test(t)) n += 10;
  if (style === 'Drill' && /\bdrill\b/i.test(t)) n += 10;
  if (/battle|batalha|freestyle|cypher/i.test(t)) n += 5;
  if (/instrumental|no vocals|beat/i.test(t)) n += 3;
  if (/underground|old\s*[-]?\s*school|90s|east\s*coast|golden\s*era/i.test(t)) n += 2;
  return n;
}
async function mapLimit(items, limit, fn) {
  const out = new Array(items.length);
  let next = 0;
  await Promise.all(Array.from({length: Math.min(limit, items.length)}, async () => {
    while (true) {
      const i = next++;
      if (i >= items.length) return;
      try { out[i] = await fn(items[i], i); }
      catch (e) { out[i] = null; console.error('CATALOG_TASK_FAIL', String(e)); }
    }
  }));
  return out;
}
async function fetchQuery(q) {
  const params = [
    ['client_id', clientId], ['format','json'], ['limit','200'],
    ['include','musicinfo+licenses'], ['imagesize','100'], ['audioformat','mp32'],
    ['audiodlformat','mp32'], ['type','single albumtrack'],
    ['vocalinstrumental','instrumental'], ['order','relevance'],
    ['boost','popularity_month']
  ];
  let url = 'https://api.jamendo.com/v3.0/tracks/?' +
    params.map(([k,v]) => k + '=' + encodeURIComponent(v).replace(/%2B/gi, '+')).join('&');
  url += '&' + q[0] + '=' +
    (q[0] === 'fuzzytags'
      ? encodeURIComponent(q[1]).replace(/%2B/gi, '+')
      : encodeURIComponent(q[1]));
  const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), 18000);
  try {
    let res, body;
    for (let attempt = 0; attempt < 4; attempt++) {
      res = await fetch(url, {signal:ctl.signal, headers:{'Accept':'application/json'}});
      body = await res.text();
      if (res.status !== 429) break;
      const delay = 1200 * (attempt + 1);
      console.log('JAMENDO_RATE_LIMIT', q[0]+'='+q[1], 'retry='+(attempt+1), 'wait=' + delay);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = JSON.parse(body);
    if (data.headers && data.headers.status && data.headers.status !== 'success')
      throw new Error('Jamendo: ' + JSON.stringify(data.headers));
    return Array.isArray(data.results) ? data.results : [];
  } finally { clearTimeout(timer); }
}
async function probeAudio(url) {
  const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), 9000);
  try {
    const res = await fetch(url, {
      headers:{Range:'bytes=0-2047', Accept:'audio/mpeg,audio/*;q=0.9,*/*;q=0.1'},
      signal:ctl.signal
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
function makeRow(style, r) {
  const license = Array.isArray(r.licenses) && r.licenses.length
    ? String(r.licenses[0].shortname || r.licenses[0].name || 'Ver licença')
    : 'Ver licença na Jamendo';
  return [
    String(r.audio || ''), String(r.name || (style + ' instrumental')).replace(/\s+/g,' ').trim(),
    0, 0, String(r.id), style, String(r.artist_name || 'Artista independente'),
    String(r.shareurl || ('https://www.jamendo.com/track/' + r.id)), license,
    String(r.audiodownload || ''),
    r.audiodownload_allowed === true && !!r.audiodownload,
    Number(r.duration) || 0
  ];
}
async function buildStyle(style) {
  const queries = CONFIG[style].queries;
  const byId = new Map();
  for (let offset = 0; offset < queries.length && byId.size < 160; offset += 5) {
    const batch = queries.slice(offset, offset + 5);
    const resultSets = await mapLimit(batch, 3, q => fetchQuery(q));
    for (const rows of resultSets) for (const r of (rows || [])) {
      if (!r || !r.id || !r.audio || !(Number(r.duration) >= 85 && Number(r.duration) <= 540)) continue;
      const score = scoreOf(style, r);
      if (score < CONFIG[style].minScore) continue;
      const id = String(r.id), old = byId.get(id);
      if (!old || score > old.score) byId.set(id, {r, score});
    }
    console.log('CATALOG_QUERY', style, offset + batch.length, '/', queries.length, 'qualified=', byId.size);
  }
  const ranked = [...byId.values()].sort((a,b) =>
    b.score - a.score || String(a.r.name).localeCompare(String(b.r.name)));
  const first = [], rest = [], artists = new Set();
  for (const x of ranked) {
    const key = String(x.r.artist_id || x.r.artist_name || '').toLowerCase();
    if (!artists.has(key)) { artists.add(key); first.push(x); } else rest.push(x);
  }
  const pool = first.concat(rest);
  const out = [];
  const seen = new Set();
  // Verifica em lotes e para assim que houver 70 streams válidos; evita testar dezenas de faixas desnecessárias.
  for (let offset = 0; offset < pool.length && out.length < TARGET; offset += 20) {
    const batch = pool.slice(offset, offset + 20);
    const checked = await mapLimit(batch, 10, async x => ({x, ok:await probeAudio(x.r.audio)}));
    for (const p of checked) {
      if (!p || !p.ok || seen.has(String(p.x.r.id))) continue;
      seen.add(String(p.x.r.id));
      out.push(makeRow(style, p.x.r));
      if (out.length >= TARGET) break;
    }
    console.log('CATALOG_AUDIO_BATCH', style, 'tested=' + Math.min(offset + batch.length, pool.length), 'valid=' + out.length + '/' + TARGET);
  }
  if (out.length < TARGET) {
    throw new Error(style + ': somente ' + out.length + '/' + TARGET +
      ' instrumentais com áudio validado no Jamendo; não vou inventar faixas.');
  }
  console.log('CATALOG_STYLE_OK', style, out.length);
  return out;
}

(async () => {
  console.log('CATALOG_SEED_START', clientId.slice(0,3) + '…', 'target=' + TARGET);
  const catalogs = {};
  for (const style of Object.keys(CONFIG)) catalogs[style] = await buildStyle(style);
  const seenAcross = new Map();
  for (const [style, rows] of Object.entries(catalogs)) {
    for (const row of rows) {
      const old = seenAcross.get(row[4]);
      if (old) throw new Error('Faixa duplicada entre estilos: ' + row[4] + ' (' + old + '/' + style + ')');
      seenAcross.set(row[4], style);
    }
  }
  const outDir = path.join(assets, 'beats');
  fs.mkdirSync(outDir, {recursive:true});
  const file = path.join(outDir, 'catalog-seed.json');
  fs.writeFileSync(file, JSON.stringify({
    version:'rimalab-full-catalog-v8',
    generatedAt:new Date().toISOString(),
    targetPerStyle:TARGET,
    vocalinstrumentalFilter:'instrumental',
    counts:Object.fromEntries(Object.entries(catalogs).map(([k,v]) => [k,v.length])),
    catalogs
  }), 'utf8');
  // Compatibilidade com o runtime antigo: deriva os 30 primeiros Boom bap do mesmo catálogo validado.
  const boomExtra = catalogs['Boom bap'].filter(row => row[11] >= 85 && row[11] <= 540).slice(0,30).map(row => ({
    id:row[4], name:row[1], audio:row[0], artist:row[6], duration:row[11],
    shareurl:row[7], license:row[8], audiodownload:row[9], audiodownload_allowed:row[10], bpm:row[2]
  }));
  fs.writeFileSync(path.join(outDir,'boom-bap-extra.json'), JSON.stringify({
    version:'rimalab-derived-boom-bap-v8', source:'Jamendo verified instrumental seed', count:boomExtra.length, tracks:boomExtra
  }), 'utf8');
  console.log('CATALOG_SEED_OK', Object.entries(catalogs).map(([k,v]) => k + '=' + v.length).join(' '));
})().catch(e => { console.error(e); process.exit(1); });
