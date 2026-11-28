#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const clientId = process.env.JAMENDO_CLIENT_ID;
if (!clientId) throw new Error('JAMENDO_CLIENT_ID não configurado');

// IDs copiados diretamente de catalog-seed.json do artefato de revisão 2026-11-28.
const ids = [
  '1881531','1757602','1876901','1922549','1398979','1363868','2136792','2195458','1781676','1963910',
  '2270818','1084630','2259989','2234444','2166633','1988935','1863767','1596137','2062462','2193316',
  '1936171','2186226','2327521','2164557','2064625','2173693','1338459','1698660','1398127','100273',
  '1482182','1667742','1138826','2024442','1694555','1232761','1683302','1589631','2012539','1669454',
  '769010','1639847','2233832','1308280','1630575','726883','1233434','1623401','1365760','1323285',
  '632632','1977559','1901604','1796614','1876905','1796775','1913125','1986516','1877237','1889057',
  '2002825','1901602','1901600','2125060','1888666','2167104','2151060','1901601','1901599','2149149',
  '2136800','2258791','2275596','2151083','1857242','1596139','1931316','1895015','1895016','1895017',
  '1895018','2193314','1895012','1895014','1895013','1895011','1892153','1991135'
];

async function fetchByIds(batch) {
  const params = new URLSearchParams({
    client_id: clientId, format: 'json', limit: '100',
    id: batch.join('+'), include: 'licenses'
  });
  const response = await fetch('https://api.jamendo.com/v3.0/tracks/?' + params, {
    headers: { accept: 'application/json' }
  });
  const body = await response.text();
  if (!response.ok) throw new Error('Jamendo HTTP ' + response.status + ': ' + body.slice(0, 300));
  const data = JSON.parse(body);
  if (data.headers?.status !== 'success') throw new Error(JSON.stringify(data.headers));
  return data.results || [];
}

function classify(url) {
  const s = String(url || '').toLowerCase();
  if (!s) return 'LICENÇA NÃO INFORMADA';
  if (/publicdomain\/zero/.test(s)) return 'CC0';
  const m = s.match(/creativecommons\.org\/licenses\/([^/]+)/);
  if (!m) return 'OUTRA LICENÇA / VERIFICAR';
  const c = m[1].toUpperCase();
  if (c.startsWith('BY-NC-ND')) return 'CC BY-NC-ND';
  if (c.startsWith('BY-NC-SA')) return 'CC BY-NC-SA';
  if (c.startsWith('BY-NC')) return 'CC BY-NC';
  if (c.startsWith('BY-ND')) return 'CC BY-ND';
  if (c.startsWith('BY-SA')) return 'CC BY-SA';
  if (c.startsWith('BY')) return 'CC BY';
  return 'OUTRA LICENÇA / VERIFICAR';
}

(async () => {
  const rows = [];
  // Lotes menores para reduzir risco de resposta truncada/limite do endpoint.
  for (let i = 0; i < ids.length; i += 10) {
    const batch = ids.slice(i, i + 10);
    let result, error;
    for (let attempt = 1; attempt <= 4; attempt++) {
      try { result = await fetchByIds(batch); break; }
      catch (e) { error = e; await new Promise(r => setTimeout(r, attempt * 1200)); }
    }
    if (!result) throw error;
    rows.push(...result);
    console.log('Lote', Math.floor(i / 10) + 1, ':', result.length, '/', batch.length);
  }
  const byId = new Map(rows.map(r => [String(r.id), r]));
  const tracks = ids.map(id => {
    const r = byId.get(id);
    if (!r) return { id, name: '', artist: '', license: 'ID NÃO RETORNADO', license_ccurl: '', audiodownload_allowed: null };
    const url = r.license_ccurl || '';
    return {
      id, name: r.name || '', artist: r.artist_name || '',
      license: classify(url), license_ccurl: url,
      audiodownload_allowed: r.audiodownload_allowed === true
    };
  });
  const counts = {};
  for (const t of tracks) counts[t.license] = (counts[t.license] || 0) + 1;
  fs.mkdirSync('audit-output', { recursive: true });
  const report = { generatedAt: new Date().toISOString(), requestedCount: ids.length, returnedCount: rows.length, counts, tracks };
  fs.writeFileSync('audit-output/boom-bap-licenses.json', JSON.stringify(report, null, 2));
  const cols = ['id','name','artist','license','license_ccurl','audiodownload_allowed'];
  fs.writeFileSync('audit-output/boom-bap-licenses.csv', [
    cols.join(','),
    ...tracks.map(t => cols.map(k => '"' + String(t[k] ?? '').replace(/"/g, '""') + '"').join(','))
  ].join('\n'));
  const summary = [
    '# Auditoria de licenças Jamendo — Boom Bap',
    '',
    '- IDs do catálogo: ' + ids.length,
    '- Faixas retornadas pela API: ' + rows.length,
    '',
    '| Licença | Quantidade |','|---|---:|',
    ...Object.entries(counts).map(([k,v]) => '| ' + k + ' | ' + v + ' |'),
    '',
    '| ID | Faixa | Artista | Licença | Download permitido |','|---|---|---|---|---|',
    ...tracks.map(t => '| ' + t.id + ' | ' + t.name.replace(/\|/g,'/') + ' | ' + t.artist.replace(/\|/g,'/') + ' | ' + t.license + ' | ' + (t.audiodownload_allowed === true ? 'Sim' : t.audiodownload_allowed === false ? 'Não' : 'Não confirmado') + ' |')
  ].join('\n');
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, summary + '\n');
  console.log(JSON.stringify({ requested: ids.length, returned: rows.length, counts }, null, 2));
  if (rows.length !== ids.length) process.exitCode = 2;
})().catch(e => { console.error(e); process.exit(1); });
