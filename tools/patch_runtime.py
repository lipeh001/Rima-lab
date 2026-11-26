#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
html_path = root / "app/src/main/assets/rima-lab.html"
main_path = root / "app/src/main/java/app/rimalab/MainActivity.java"
service_path = root / "app/src/main/java/app/rimalab/MusicService.java"

def replace_once(text, old, new, label):
    if old not in text:
        if new in text:
            return text
        raise SystemExit("PATCH_FAIL: trecho não encontrado: " + label)
    return text.replace(old, new, 1)

html = html_path.read_text(encoding="utf-8")

# Instrução clara da biblioteca: não orientar o usuário a tocar em uma seta.
html = replace_once(
    html,
    "Escolha uma base para ouvir e treinar. Toque na seta para salvar no celular.",
    "Escolha uma base para ouvir e treinar. Depois de ouvir, você pode salvar o beat no celular para usar offline.",
    "instrução de salvamento da biblioteca"
)

# 1) Rejeita a faixa de Drill que o usuário identificou como música cantada.
html = replace_once(
    html,
    "function zBuild(st){const L=(ZRAW[st]||[]).slice(),seen=new Set(L.map(x=>String(x[4])));",
    "function zBuild(st){const L=(ZRAW[st]||[]).filter(x=>!(st==='Drill'&&/with\\s+some\\s+money|all\\$?tarv/i.test(String(x[1]||'')+' '+String(x[6]||'')))).slice(),seen=new Set(L.map(x=>String(x[4])));",
    "filtro da música indevida em Drill"
)

# 2) Bloqueia registros que o Jamendo marcou como vocais; preserva apenas instrumentais.
html = replace_once(
    html,
    "function zJmRank(st,r){const t=zJmTxt(r),x=ZRX[st];if(x.ban.test(t))return 9;if(x.strong.test(t))return 0;if(x.base.test(t))return 1;return 2}",
    "function zJmRank(st,r){const mi=r&&r.musicinfo||{},vi=String(mi.vocalinstrumental||'').toLowerCase(),t=zJmTxt(r),x=ZRX[st];if(vi&&vi!=='instrumental')return 9;if(st==='Drill'&&/with\\s+some\\s+money|all\\$?tarv/i.test(t))return 9;if(x.ban.test(t))return 9;return x.strong.test(t)?0:9}",
    "validação de faixa instrumental"
)

# Jamendo aceita include como lista separada por '+', não por vírgula.
html = replace_once(
    html,
    "&include=musicinfo%2Clicenses&imagesize=100",
    "&include=licenses+musicinfo&imagesize=100",
    "formato correto do parâmetro include do Jamendo"
)

# 3) Invalida a busca antiga uma única vez. Os beats já salvos continuam visíveis.
html = replace_once(
    html,
    "const ZCACHE_MS=12*60*60*1000;",
    "const ZCACHE_MS=12*60*60*1000;\nconst ZCATALOG_VERSION='rimalab-verified-instrumental-v4-20261125';try{if(localStorage.getItem('rima_jamendo_search_version')!==RIMA_BALANCED_CATALOG_VERSION){['Boom bap','Trap','Drill'].forEach(st=>localStorage.removeItem('jmraw8_at_'+st));localStorage.setItem('rima_jamendo_search_version',ZCATALOG_VERSION)}}catch(e){}",
    "versão do cache Jamendo"
)

# 4) Carrega 30 beats extra verificados do Jamendo, empacotados durante o build.
boot_old = "function zBootCatalog(){if(!navigator.onLine)return;['Boom bap','Trap','Drill'].forEach(st=>{if(!ZJS[st]||ZJS[st]==='off'||ZJS[st]==='err'||ZJS[st]==='nokey')zJm(st)})}"
boot_new = """async function zLoadVerifiedBoomBap(){try{const r=await fetch('beats/boom-bap-extra.json',{cache:'no-store'});if(!r.ok)return;const j=await r.json();if(!j||!Array.isArray(j.tracks))return;const L=ZRAW['Boom bap']||(ZRAW['Boom bap']=[]),seen=new Set(L.map(x=>String(x[4])));for(const t of j.tracks){if(!t||!t.id||!t.audio||seen.has(String(t.id)))continue;L.push([String(t.audio),String(t.name||'Boom bap instrumental'),Number(t.bpm)||0,0,String(t.id),'Boom bap',String(t.artist||'Artista independente'),String(t.shareurl||('https://www.jamendo.com/track/'+t.id)),String(t.license||'Ver licença'),String(t.audiodownload||''),t.audiodownload_allowed===true&&!!t.audiodownload]);seen.add(String(t.id))}zSv('jmraw8',ZRAW);zBuild('Boom bap');if(ZS.s==='Boom bap')pk();window.rimaBoomBapExtraCount=seen.size}catch(e){window.rimaBoomBapExtraError=String(e)}}\nfunction zBootCatalog(){zLoadVerifiedBoomBap();if(!navigator.onLine)return;['Boom bap','Trap','Drill'].forEach(st=>{if(ZCATALOG_FORCE_REFRESH||!ZJS[st]||ZJS[st]==='off'||ZJS[st]==='err'||ZJS[st]==='nokey')zJm(st)})}"""
html = replace_once(html, boot_old, boot_new, "carregamento do catálogo extra")

# Desativa o reinício do treino ao trocar de faixa; a troca deve atuar somente no player.
html = re.sub(r"(?<!function )zRestartAct\(\)", "false", html)

# 5) Troca de faixa: não redesenha a lista duas vezes nem força scroll para o topo.
html = replace_once(
    html,
    "if($('#lv')&&!$('#lv').hidden){ZNR=1;lvStart();return true}",
    "if($('#lv')&&!$('#lv').hidden){ZNR=1;window.__rimaNoAutoScroll=1;try{lvStart()}finally{window.__rimaNoAutoScroll=0}return true}",
    "reinício sem salto de tela"
)
swap_old = "function zSwap(){if(play){if(!zRestartAct()){zLoad(ZS.k=='syn'?zBars():0);pk()}return}pk()}"
swap_new = "function zSwap(){if(play){zLoad(ZS.k=='syn'?zBars():0);pk();return}pk()}"
if swap_old in html:
    html = html.replace(swap_old, swap_new, 1)
elif swap_new not in html:
    print("Aviso: zSwap não correspondeu às variantes conhecidas; mantendo implementação existente.")
wrapper_old = "(function(){['go','lvStart','lvStop','bhome','solo'].forEach(n=>{const f=window[n];if(typeof f!='function')return;window[n]=function(){const r=f.apply(this,arguments);try{window.scrollTo(0,0)}catch(e){}return r}})})();"
wrapper_new = "(function(){['go','bhome','solo'].forEach(n=>{const f=window[n];if(typeof f!='function')return;window[n]=function(){const r=f.apply(this,arguments);if(!window.__rimaNoAutoScroll)try{window.scrollTo(0,0)}catch(e){}return r}})})();"
html = replace_once(html, wrapper_old, wrapper_new, "controle de scroll")
html = replace_once(
    html,
    "if(a=='prev'){zStep(-1);return}if(a=='next'){zStep(1);return}if(a=='pause'&&zPL)zToggle();else if(a=='play'&&!zPL)zToggle()",
    "if(a=='prev'){zStep(-1);return}if(a=='next'){zStep(1);return}if(a=='stop'){stop();return}if(a=='pause'&&zPL)zToggle();else if(a=='play'&&!zPL)zToggle()",
    "comando parar da notificação"
)

# 6) Luz apenas na moldura, nunca no desenho das letras.
style = r"""
<style id="rima-runtime-v4">
/* Paisagem: player compacto em uma única linha e palco sempre livre para as palavras. */
@media (orientation:landscape) and (max-height:640px) {
  body.pl main { padding-bottom:calc(122px + env(safe-area-inset-bottom,0px))!important; }
  #lv:not([hidden]) { display:grid!important; grid-template-columns:minmax(0,1.65fr) minmax(0,1fr)!important; gap:8px 12px!important; align-items:stretch!important; }
  #lv>.stage { grid-column:1!important; grid-row:1 / span 3!important; min-height:clamp(168px,calc(100svh - 154px),340px)!important; height:100%!important; margin:0!important; align-self:stretch!important; }
  #lv>.bk { grid-column:2!important; grid-row:1!important; width:100%!important; }
  #lv>.card:not(.stage) { grid-column:2!important; grid-row:2!important; min-width:0!important; }
  #lv>.btn.w { grid-column:2!important; grid-row:3!important; width:100%!important; }
  #lv>*:not(.stage) { min-width:0!important; }
  #pbar { left:10px!important; right:10px!important; bottom:calc(58px + env(safe-area-inset-bottom,0px))!important; width:auto!important; max-width:none!important; height:52px!important; min-height:52px!important; padding:4px 8px!important; display:flex!important; flex-direction:row!important; align-items:center!important; gap:7px!important; border-radius:14px!important; }
  #pbar .pwrow { min-width:0!important; flex:1 1 auto!important; min-height:40px!important; gap:6px!important; }
  #pbar .pw-art { display:none!important; }
  #pbar .pw-controls { flex:0 0 auto!important; gap:1px!important; }
  #pbar .pw-controls button { width:26px!important; height:30px!important; }
  #pbar .pw-controls #pwb { width:34px!important; height:34px!important; }
  #pbar .pwi { min-width:0!important; flex:1 1 auto!important; }
  #pbar .pwi b { display:block!important; font-size:11px!important; overflow:hidden!important; text-overflow:ellipsis!important; white-space:nowrap!important; }
  #pbar .pwi small { display:none!important; }
  #pbar .pws { width:27px!important; height:27px!important; flex:0 0 27px!important; }
  #pbar .pwinfo,#pbar .pwscr { display:none!important; }
  nav { z-index:100!important; min-height:50px!important; padding:3px 8px calc(3px + env(safe-area-inset-bottom,0px))!important; }
  nav button { min-height:43px!important; }
}
@media (orientation:landscape) and (max-height:420px) {
  body.pl main { padding-bottom:calc(112px + env(safe-area-inset-bottom,0px))!important; }
  #pbar { height:46px!important; min-height:46px!important; bottom:calc(52px + env(safe-area-inset-bottom,0px))!important; }
  #pbar .pw-controls button { width:23px!important; height:27px!important; }
  #pbar .pw-controls #pwb { width:30px!important; height:30px!important; }
  nav button { min-height:38px!important; }
}
/* A pulsação aumenta a luz da borda; a tipografia do palco permanece estável e nítida. */
#stg.stage { border:1px solid rgba(215,251,87,.28)!important; box-shadow:0 0 0 1px rgba(215,251,87,.06),inset 0 0 22px rgba(215,251,87,.035)!important; }
#stg.stage::after { content:""!important; display:block!important; position:absolute!important; inset:1px!important; z-index:3!important; pointer-events:none!important; border:1px solid rgba(215,251,87,.16)!important; border-radius:inherit!important; opacity:.35!important; box-shadow:inset 0 0 20px rgba(215,251,87,.10),0 0 12px rgba(215,251,87,.07)!important; }
#stg.stage.hit { border-color:rgba(215,251,87,.92)!important; box-shadow:0 0 0 1px rgba(215,251,87,.30),0 0 30px rgba(215,251,87,.34),inset 0 0 30px rgba(215,251,87,.11)!important; }
#stg.stage.hit::after { animation:rl-edge-energy .46s ease-out!important; }
@keyframes rl-edge-energy { 0% { opacity:1; border-color:rgba(230,255,135,.98)!important; box-shadow:inset 0 0 34px rgba(215,251,87,.25),0 0 34px rgba(215,251,87,.40)!important; } 100% { opacity:.24; border-color:rgba(215,251,87,.22)!important; box-shadow:inset 0 0 9px rgba(215,251,87,.04),0 0 5px rgba(215,251,87,.03)!important; } }
@media (prefers-reduced-motion:reduce) { #stg.stage.hit::after { animation:none!important; opacity:.28!important; } }
</style>
"""
if 'id="rima-runtime-v4"' not in html:
    html = html.replace("</head>", style + "\n</head>", 1)

html_path.write_text(html, encoding="utf-8")

# Incrementa a versão sem alterar applicationId nem a configuração de assinatura Gradle.
gradle_path = root / "app/build.gradle"
gradle = gradle_path.read_text(encoding="utf-8")
if "versionCode 19" in gradle:
    gradle = replace_once(gradle, "versionCode 19", "versionCode 22", "versionCode 2.8.5")
elif "versionCode 20" in gradle:
    gradle = replace_once(gradle, "versionCode 20", "versionCode 22", "versionCode 2.8.5")
else:
    raise SystemExit("PATCH_FAIL: versionCode inesperado no projeto Gradle")
if "versionName '2.8.3'" in gradle:
    gradle = replace_once(gradle, "versionName '2.8.3'", "versionName '2.8.5'", "versionName 2.8.5")
elif "versionName '2.8.4'" in gradle:
    gradle = replace_once(gradle, "versionName '2.8.4'", "versionName '2.8.5'", "versionName 2.8.5")
else:
    raise SystemExit("PATCH_FAIL: versionName inesperado no projeto Gradle")
gradle_path.write_text(gradle, encoding="utf-8")

# 7) Notification permission/channel handling: keep the paused notification visible.
main = main_path.read_text(encoding="utf-8")
main = replace_once(
    main,
    """    private boolean notifOn() {
        try { return ((android.app.NotificationManager) getSystemService(NOTIFICATION_SERVICE)).areNotificationsEnabled(); }
        catch (Exception e) { return false; }
    }""",
    """    private boolean notifOn() {
        try {
            android.app.NotificationManager nm = (android.app.NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (!nm.areNotificationsEnabled()) return false;
            if (android.os.Build.VERSION.SDK_INT >= 26) {
                android.app.NotificationChannel ch = nm.getNotificationChannel(MusicService.CH);
                if (ch != null && ch.getImportance() == android.app.NotificationManager.IMPORTANCE_NONE) return false;
            }
            return true;
        } catch (Exception e) { return false; }
    }""",
    "verificação do canal de notificações"
)
main = replace_once(
    main,
    """            if (st <= 0) { c.stopService(new Intent(c, MusicService.class)); return; }
            if (!notifOn()) return;
            try { c.startForegroundService(new Intent(c, MusicService.class).putExtra("st", 1).putExtra("title", title)); } catch (Exception e) {}""",
    """            if (st < 0) { c.stopService(new Intent(c, MusicService.class)); return; }
            if (!notifOn()) return;
            try { c.startForegroundService(new Intent(c, MusicService.class).putExtra("st", st).putExtra("title", title)); } catch (Exception e) {}""",
    "estado pausado mantém notificação"
)
main_path.write_text(main, encoding="utf-8")

# 8) MediaSession real para o Android exibir o cartão de mídia com controles consistentes.
service = service_path.read_text(encoding="utf-8")
service = replace_once(service, 'static final String CH = "rimalab_player_v2";', 'static final String CH = "rimalab_player_v3";', "novo canal de mídia")
if "import android.media.session.MediaSession;" not in service:
    service = service.replace("import android.app.Service;", "import android.app.Service;\nimport android.media.MediaMetadata;\nimport android.media.session.MediaSession;\nimport android.media.session.PlaybackState;")
service = replace_once(
    service,
    "    static final int ID = 7;\n\n    @Override public IBinder onBind(Intent i) { return null; }",
    """    static final int ID = 7;
    private MediaSession mediaSession;

    @Override public void onCreate() {
        super.onCreate();
        mediaSession = new MediaSession(this, "RimaLabMedia");
        mediaSession.setFlags(MediaSession.FLAG_HANDLES_MEDIA_BUTTONS | MediaSession.FLAG_HANDLES_TRANSPORT_CONTROLS);
        mediaSession.setCallback(new MediaSession.Callback() {
            @Override public void onPlay() { MainActivity.remote("play"); }
            @Override public void onPause() { MainActivity.remote("pause"); }
            @Override public void onSkipToPrevious() { MainActivity.remote("prev"); }
            @Override public void onSkipToNext() { MainActivity.remote("next"); }
            @Override public void onStop() { MainActivity.remote("stop"); stopForeground(true); stopSelf(); }
        });
    }

    @Override public IBinder onBind(Intent i) { return null; }

    private void syncSession(boolean playing, String title) {
        if (mediaSession == null) return;
        mediaSession.setMetadata(new MediaMetadata.Builder()
                .putString(MediaMetadata.METADATA_KEY_TITLE, title)
                .putString(MediaMetadata.METADATA_KEY_ARTIST, "Rima Lab · Treino de freestyle")
                .putString(MediaMetadata.METADATA_KEY_ALBUM, "Biblioteca de beats")
                .build());
        long actions = PlaybackState.ACTION_PLAY | PlaybackState.ACTION_PAUSE | PlaybackState.ACTION_PLAY_PAUSE
                | PlaybackState.ACTION_SKIP_TO_NEXT | PlaybackState.ACTION_SKIP_TO_PREVIOUS | PlaybackState.ACTION_STOP;
        PlaybackState state = new PlaybackState.Builder()
                .setActions(actions)
                .setState(playing ? PlaybackState.STATE_PLAYING : PlaybackState.STATE_PAUSED,
                        0L, playing ? 1f : 0f, android.os.SystemClock.elapsedRealtime())
                .build();
        mediaSession.setPlaybackState(state);
        if (!mediaSession.isActive()) mediaSession.setActive(true);
    }""",
    "MediaSession"
)
service = replace_once(
    service,
    """        boolean playing = in != null && in.getIntExtra("st", 0) == 1;
        String title = in != null ? in.getStringExtra("title") : null;
        if (title == null || title.length() == 0) title = "Rima Lab";
        Notification n = build(playing, title);""",
    """        boolean playing = in != null && in.getIntExtra("st", 0) == 1;
        String title = in != null ? in.getStringExtra("title") : null;
        if (title == null || title.length() == 0) title = "Rima Lab";
        syncSession(playing, title);
        Notification n = build(playing, title);""",
    "sincronização da sessão de mídia"
)
service = replace_once(
    service,
    """        if (A_STOP.equals(a)) {
            MainActivity.remote("pause");
            stopForeground(true); stopSelf();
            return START_NOT_STICKY;
        }""",
    """        if (A_STOP.equals(a)) {
            MainActivity.remote("stop");
            stopForeground(true); stopSelf();
            return START_NOT_STICKY;
        }""",
    "ação encerrar player"
)
service = replace_once(
    service,
    """            c.setDescription("Controles do beat enquanto você treina em segundo plano.");
            c.setShowBadge(false);
            c.enableVibration(false);
            c.setSound(null, null);
            nm.createNotificationChannel(c);""",
    """            c.setDescription("Player do Rima Lab: faixa atual, anterior, próxima e pausar/tocar.");
            c.setShowBadge(false);
            c.enableVibration(false);
            c.setSound(null, null);
            c.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
            nm.createNotificationChannel(c);""",
    "descrição do canal"
)
service = replace_once(
    service,
    """.setContentText("Rima Lab · " + (playing ? "Beat em reprodução" : "Player pausado"))""",
    """.setContentText(playing ? "Reproduzindo · Treino de freestyle" : "Pausado · toque para continuar")""",
    "texto da notificação"
)
service = replace_once(
    service,
    """.setVisibility(Notification.VISIBILITY_PRIVATE)""",
    """.setVisibility(Notification.VISIBILITY_PUBLIC)""",
    "visibilidade na tela bloqueada"
)
service = replace_once(
    service,
    """.setStyle(new Notification.MediaStyle().setShowActionsInCompactView(0, 1, 2))""",
    """.setStyle(new Notification.MediaStyle().setMediaSession(mediaSession.getSessionToken()).setShowActionsInCompactView(0, 1, 2))""",
    "cartão MediaStyle conectado à sessão"
)
if "mediaSession.release();" not in service:
    service = service.replace(
        """    /** Capa do beat: quadrado arredondado em degradê roxo com barras de onda sonora. */""",
        """    @Override public void onDestroy() {
        try { if (mediaSession != null) { mediaSession.setActive(false); mediaSession.release(); mediaSession = null; } } catch (Exception e) {}
        super.onDestroy();
    }

    /** Capa do beat: quadrado arredondado em degradê verde com barras de onda sonora. */"""
    )
service_path.write_text(service, encoding="utf-8")


# 9) Limites por categoria aplicados no momento de montar a lista.
# A função real do projeto pode variar; injeta um limitador na atribuição final.
if "window.rimaCatalogCapsV1" not in html:
    html = html.replace("</script>", """
// Rima Lab: limites de catálogo para evitar acumular resultados antigos.
window.rimaCatalogCapsV1 = true;
const rimaCapCatalog = () => {
  try {
    const caps = {'Boom bap': 75, 'Trap': 100, 'Drill': 21};
    if (typeof ZLIB === 'object' && typeof ZRAW === 'object') {
      Object.keys(caps).forEach(st => {
        if (Array.isArray(ZLIB[st]?.[1])) ZLIB[st][1] = ZLIB[st][1].slice(0, caps[st]);
      });
    }
  } catch(e) {}
};
""" + "</script>", 1)

# 10) Mensagem: salvamento automático é tentado ao iniciar a primeira reprodução,
# somente para faixas cuja licença permite download.
html = html.replace(
    "Escolha uma base para ouvir e treinar. Toque na seta para salvar no celular.",
    "Escolha uma base para ouvir e treinar. Na primeira reprodução, o app tenta salvar o beat automaticamente para ouvir offline, se a licença permitir."
)

# 11) Palco: reduzir o flash, remover a animação do texto e manter um pulso suave.
html = html.replace(
    ".stage.hit .word{animation:rl-word-crisp .18s cubic-bezier(.2,.75,.25,1)!important;filter:none!important}\\n@keyframes rl-word-crisp{from{opacity:.88;transform:translateY(3px) scale(.99);filter:none}to{opacity:1;transform:translateY(0) scale(1);filter:none}}",
    ".stage.hit .word{animation:none!important;filter:none!important;transform:none!important;opacity:1!important}\\n.stage.hit{animation:rl-stage-soft .52s ease-out!important}\\n@keyframes rl-stage-soft{0%{border-color:rgba(215,251,87,.58);box-shadow:inset 0 0 16px rgba(215,251,87,.045),0 0 10px rgba(215,251,87,.10)}100%{border-color:rgba(255,255,255,.08);box-shadow:inset 0 1px rgba(255,255,255,.035),0 14px 34px rgba(0,0,0,.28)}}"
)

# 12) Reaplicar e GRAVAR as correções finais depois dos blocos legados.
html = html_path.read_text(encoding="utf-8")
cache_fix = """const RIMA_BALANCED_CATALOG_VERSION='rimalab-balanced-catalog-v6';try{if(localStorage.getItem('rima_catalog_version')!==RIMA_BALANCED_CATALOG_VERSION){['jmraw7','jmraw6','jmraw7_at_Boom bap','jmraw7_at_Trap','jmraw7_at_Drill'].forEach(k=>localStorage.removeItem(k));localStorage.setItem('rima_catalog_version',RIMA_BALANCED_CATALOG_VERSION)}}catch(e){}"""
if "rimalab-balanced-catalog-v6" not in html:
    html = html.replace("const ZCACHE_MS=12*60*60*1000;", "const ZCACHE_MS=12*60*60*1000;\n"+cache_fix, 1)

html = html.replace("function zCacheFresh(st){try{const rows=Array.isArray(ZRAW[st])?ZRAW[st].length:0;return rows>=50&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS}catch(e){return false}}",
"function zCacheFresh(st){try{const cap=st==='Boom bap'?70:st==='Trap'?70:20,rows=Array.isArray(ZRAW[st])?ZRAW[st].length:0;return rows>=cap&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS}catch(e){return false}}")
html = html.replace("ZRAW[st]=merged.slice(0,50)", "ZRAW[st]=merged.slice(0,st==='Boom bap'?70:st==='Trap'?70:20)")
html = html.replace("ZLIB[st][1]=L.slice(0,50)", "ZLIB[st][1]=L.slice(0,st==='Boom bap'?70:st==='Trap'?70:20)")
html = html.replace("if(picked.length>=50)break", "if(picked.length>=(st==='Boom bap'?70:st==='Trap'?70:20))break")
html = html.replace("if(picked.length<50)", "if(picked.length<(st==='Boom bap'?70:st==='Trap'?70:20))")
html = html.replace("if(merged.length>=50)break", "if(merged.length>=(st==='Boom bap'?70:st==='Trap'?70:20))break")
html = html.replace("\${ZLIB[s][1].length}/50", "\${ZLIB[s][1].length}/\${s==='Boom bap'?70:s==='Trap'?70:20}")
html = html.replace("Escolha uma base para ouvir e treinar. Toque na seta para salvar no celular.", "Escolha uma base para ouvir e treinar. Na primeira vez que você ouvir, o app tenta salvar o beat automaticamente para ouvir offline, quando a licença permite.")
html = html.replace(".stage.hit .word{animation:rl-word-crisp .18s cubic-bezier(.2,.75,.25,1)!important;filter:none!important}", ".stage.hit .word{animation:rl-word-soft .48s ease-out!important;filter:none!important}")
html = html.replace("@keyframes rl-word-crisp{from{opacity:.88;transform:translateY(3px) scale(.99);filter:none}to{opacity:1;transform:translateY(0) scale(1);filter:none}}", "@keyframes rl-word-soft{0%{opacity:.94;transform:scale(.995)}100%{opacity:1;transform:scale(1)}}")
html = html.replace(".stage::after{display:none!important;animation:none!important;box-shadow:none!important}", ".stage::after{display:block!important;animation:none!important;box-shadow:inset 0 0 18px rgba(215,251,87,.07)!important;opacity:.35!important}")
html = html.replace(".stage.hit::after{display:none!important;animation:none!important}", ".stage.hit::after{display:block!important;animation:rl-stage-glow .72s ease-out!important}")
html = html.replace("@media(prefers-reduced-motion:reduce){.stage.hit .word{animation:none!important}", "@keyframes rl-stage-glow{0%{opacity:.75;box-shadow:inset 0 0 28px rgba(215,251,87,.18),0 0 16px rgba(215,251,87,.15)}100%{opacity:.18;box-shadow:inset 0 0 8px rgba(215,251,87,.04),0 0 3px rgba(215,251,87,.02)}}\n@media(prefers-reduced-motion:reduce){.stage.hit .word{animation:none!important}")
html_path.write_text(html, encoding="utf-8")

icon_path = root / "app/src/main/res/drawable/ic_stat_beat.xml"
icon_path.write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M5,3h8.1c4.1,0 6.4,2.1 6.4,5.6 0,2.5 -1.2,4.2 -3.4,5l3.9,7.4h-4.5l-3.4,-6.8H9v6.8H5V3zM9,6.6v4.2h4c1.7,0 2.5,-0.7 2.5,-2.1 0,-1.4 -0.8,-2.1 -2.5,-2.1H9z"/>
</vector>''', encoding="utf-8")

gradle_path = root / "app/build.gradle"
gradle = gradle_path.read_text(encoding="utf-8")
if "versionCode 22" in gradle: gradle = gradle.replace("versionCode 22", "versionCode 23", 1)
if "versionName '2.8.5'" in gradle: gradle = gradle.replace("versionName '2.8.5'", "versionName '2.8.6'", 1)
gradle_path.write_text(gradle, encoding="utf-8")

# 13) Aplicar os limites aos trechos reais desta versão do HTML.
html = html_path.read_text(encoding="utf-8")
html = html.replace(
 "function zCacheFresh(st){try{const rows=Array.isArray(ZRAW[st])?ZRAW[st].length:0;return rows>0&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS}catch(e){return false}}",
 "function zCacheFresh(st){try{const cap=st==='Boom bap'?70:st==='Trap'?70:20,rows=Array.isArray(ZRAW[st])?ZRAW[st].length:0;return rows>=cap&&Date.now()-(+localStorage.getItem('jmraw7_at_'+st)||0)<ZCACHE_MS}catch(e){return false}}"
)
html = html.replace(
 "ZLIB[st][1]=L}",
 "ZLIB[st][1]=L.slice(0,st==='Boom bap'?70:st==='Trap'?70:20)}"
)
html = html.replace(
 "if(!artistSet.has(a)){artistSet.add(a);picked.push(o)}/* sem teto de resultados */}",
 "if(!artistSet.has(a)){artistSet.add(a);picked.push(o);if(picked.length>=(st==='Boom bap'?70:st==='Trap'?70:20))break}}"
)
html = html.replace(
 "for(const o of ranked){if(picked.some(p=>String(p.r.id)==String(o.r.id)))continue;picked.push(o)}",
 "for(const o of ranked){if(picked.some(p=>String(p.r.id)==String(o.r.id)))continue;picked.push(o);if(picked.length>=(st==='Boom bap'?70:st==='Trap'?70:20))break}"
)
html = html.replace(
 "merged.push(x);/* sem teto de resultados */}",
 "merged.push(x);if(merged.length>=(st==='Boom bap'?70:st==='Trap'?70:20))break}"
)
html = html.replace(
 "Depois de ouvir, você pode salvar o beat no celular para usar offline.",
 "Na primeira vez que você ouvir, o app tenta salvar o beat automaticamente para ouvir offline, quando a licença permite."
)
html_path.write_text(html, encoding="utf-8")

print("RUNTIME_PATCH_OK: catalogo 70/70/20, cache limpo, icone R, texto e palco suave.")

print("RUNTIME_PATCH_OK: paisagem, borda pulsante, troca sem salto, filtro de Drill e notificação MediaSession.")
