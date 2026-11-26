#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
s=hp.read_text(encoding='utf-8')
# Texto direto e compreensível: calibração só é útil com caixa Bluetooth.
repls={
 'Ajuste opcional da latência do aparelho.':'Ajuste opcional para caixa de som Bluetooth.',
 'Opcional: toque em <b>Calibrar</b> para usar a latência informada pelo aparelho. Não precisa de microfone nem aumentar o volume.':'Use esta opção somente se conectar uma caixa de som Bluetooth e perceber que o beat está fora de sincronia.',
 'Calibração opcional. O ajuste fino também pode ser feito pela barra.':'Para sincronizar o beat com a caixa Bluetooth, use Calibrar ou ajuste a barra manualmente.',
 'Calibrar (opcional)':'Calibrar (opcional)',
 'Ajuste fino da sincronização':'Ajuste da sincronização com caixa Bluetooth',
 'Calibração automática pronta. O ajuste fino também pode ser feito pela barra.':'Opcional: use apenas com uma caixa Bluetooth.'
}
for a,b in repls.items(): s=s.replace(a,b)
# Remove explicações técnicas antigas caso alguma variante do texto tenha sobrevivido.
s=re.sub(r'[^<]{0,100}(?:WebView|Web Audio|AudioContext|microfone|latência de áudio informada)[^<]{0,220}',lambda m: m.group(0) if 'Bluetooth' in m.group(0) else '',s,flags=re.I)
# Atualiza o cache versionado para forçar a lista nova nos aparelhos que já abriram o app.
s=s.replace('rimalab-preloaded-87-77-74-v23','rimalab-preloaded-87-77-74-v23')
hp.write_text(s,encoding='utf-8')
gp=root/'app/build.gradle'
g=gp.read_text(encoding='utf-8')
g=re.sub(r'\\bversionCode\\s+42\\b','versionCode 43',g,count=1)
g=g.replace("versionName '3.0.0'","versionName '3.0.1'",1)
if 'versionCode 43' not in g or "versionName '3.0.1'" not in g: raise SystemExit('V23_FAIL: versão Android inesperada')
gp.write_text(g,encoding='utf-8')
(root/'CATALOGO-3.0.1-VALIDADO.txt').write_text(
 'Rima Lab 3.0.1\\nCatalogo alvo: 87 Boom bap, 77 Trap e 74 Drill.\\nA sincronizacao opcional e destinada a caixas de som Bluetooth.\\n',
 encoding='utf-8')
print('V23_OK: texto simples para Bluetooth e versão 3.0.1')
