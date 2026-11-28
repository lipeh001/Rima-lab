#!/usr/bin/env node
'use strict';

const fs = require('node:fs');

const clientId = process.env.JAMENDO_CLIENT_ID;
if (!clientId) throw new Error('JAMENDO_CLIENT_ID não configurado');

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

const chunks = [];
for (let i = 0; i < ids.length; i += 20) chunks.push(ids.slice(i, i + 20));

async function getChunk(chunk) {
  const params = new URLSearchParams({
    client_id: clientId,
    format: 'json',
    limit: '100',
    id: chunk.join('+'),
    include: 'licenses'
  });
  const url = 'https://api.jamendo.com/v3.0/tracks/?' + params.toString();
  let lastError;
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const response = await fetch(url, { headers: { accept: 'application/json' } });
      const body = await response.text();
      if (!response.ok) throw new Error('HTTP ' + response.status + ': ' + body.slice(0, 500));
      const data = JSON.parse(body);
      if (data.headers?.status !== 'success') {
        throw new Error(data.headers?.error_message || 'Resposta Jamendo sem status success');
      }
      return data.results || [];
    } catch (error) {
      lastError = error;
      await new Promise(resolve => setTimeout(resolve, attempt * 1500));
    }
  }
  throw lastError;
}

function classify(url) {
  const s = String(url || '').toLowerCase();
  if (!s) return 'LICENÇA NÃO INFORMADA';
  if (/publicdomain\/zero|creativecommons\.org\/publicdomain\/zero/.test(s)) return 'CC0';
  const match = s.match(/creativecommons\.org\/licenses\/([^/]+)/);
  if (!match) return 'OUTRA LICENÇA / VERIFICAR';
  const code = match[1].toUpperCase();
  if (code.startsWith('BY-NC-ND')) return 'CC BY-NC-ND';
  if (code.startsWith('BY-NC-SA')) return 'CC BY-NC-SA';
  if (code.startsWith('BY-NC')) return 'CC BY-NC';
  if (code.startsWith('BY-ND')) return 'CC BY-ND';
  if (code.startsWith('BY-SA')) return 'CC BY-SA';
  if (code.startsWith('BY')) return 'CC BY';
  return 'OUTRA LICENÇA / VERIFICAR';
}

(async () => {
  const all = [];
  for (const chunk of chunks) {
    const rows = await getChunk(chunk);
    all.push(...rows);
    console.log('Consultadas', chunk.length, 'IDs; retornaram', rows.length, 'faixas');
  }

  const byId = new Map(all.map(row => [String(row.id), row]));
  const results = ids.map(id => {
    const row = byId.get(id);
    if (!row) return {
      id, name: '', artist: '', license_ccurl: '', license: 'ID NÃO RETORNADO',
      audiodownload_allowed: null, audiodownload: ''
    };
    const url = row.license_ccurl || '';
    return {
      id,
      name: row.name || '',
      artist: row.artist_name || '',
      license_ccurl: url,
      license: classify(url),
      audiodownload_allowed: row.audiodownload_allowed === true,
      audiodownload: row.audiodownload || ''
    };
  });

  const missing = results.filter(row => row.license === 'ID NÃO RETORNADO');
  if (missing.length) console.warn('IDs não retornados:', missing.map(x => x.id).join(', '));

  const counts = {};
  for (const row of results) counts[row.license] = (counts[row.license] || 0) + 1;
  const report = {
    generatedAt: new Date().toISOString(),
    requestedCount: ids.length,
    returnedCount: results.length - missing.length,
    counts,
    tracks: results
  };
  fs.mkdirSync('audit-output', { recursive: true });
  fs.writeFileSync('audit-output/boom-bap-licenses.json', JSON.stringify(report, null, 2));
  const columns = ['id','name','artist','license','license_ccurl','audiodownload_allowed','audiodownload'];
  const csv = [columns.join(','), ...results.map(row => columns.map(key => {
    const value = row[key] == null ? '' : String(row[key]);
    return '"' + value.replace(/"/g, '""') + '"';
  }).join(','))].join('\n');
  fs.writeFileSync('audit-output/boom-bap-licenses.csv', csv);
  const summary = [
    '# Auditoria de licenças Jamendo — Boom Bap',
    '',
    '- IDs solicitados: ' + ids.length,
    '- Faixas retornadas: ' + (results.length - missing.length),
    '',
    '| Licença | Quantidade |',
    '|---|---:|',
    ...Object.entries(counts).map(([license, count]) => '| ' + license + ' | ' + count + ' |'),
    '',
    '| ID | Faixa | Artista | Licença | Download permitido |',
    '|---|---|---|---|---|',
    ...results.map(row => '| ' + row.id + ' | ' + row.name.replace(/\|/g, '/') + ' | ' + row.artist.replace(/\|/g, '/') + ' | ' + row.license + ' | ' + (row.audiodownload_allowed === true ? 'Sim' : row.audiodownload_allowed === false ? 'Não' : 'Não confirmado') + ' |')
  ].join('\n');
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, summary + '\n');
  console.log(JSON.stringify({ requested: ids.length, returned: results.length - missing.length, counts }, null, 2));
  if (missing.length) process.exitCode = 2;
})().catch(error => {
  console.error(error);
  process.exit(1);
});
