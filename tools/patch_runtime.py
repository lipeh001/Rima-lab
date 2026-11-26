#!/usr/bin/env python3
from pathlib import Path
import sys
import re

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


# 8a) MediaSession recebe posição/duração reais e permanece ativa durante a troca de faixa.
main = main_path.read_text(encoding="utf-8")
main = replace_once(
    main,
    """        @JavascriptInterface public void mediaState(int st, String title) {
            android.content.Context c = getApplicationContext();""",
    """        @JavascriptInterface public void mediaState(int st, String title, double duration, double position) {
            android.content.Context c = getApplicationContext();""",
    "bridge com posição e duração"
)
main = replace_once(
    main,
    """            try { c.startForegroundService(new Intent(c, MusicService.class).putExtra("st", st).putExtra("title", title)); } catch (Exception e) {}""",
    """            try {
                Intent update = new Intent(c, MusicService.class)
                        .putExtra("st", st).putExtra("title", title)
                        .putExtra("duration", (long)(Math.max(0, duration) * 1000d))
                        .putExtra("position", (long)(Math.max(0, position) * 1000d));
                c.startForegroundService(update);
            } catch (Exception e) {}""",
    "extras de duração e posição"
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

    private long currentDuration, currentPosition;
    private long getIntentDuration() { return currentDuration; }
    private void syncSession(boolean playing, String title) {
        if (mediaSession == null) return;
        long duration = getIntentDuration();
        mediaSession.setMetadata(new MediaMetadata.Builder()
                .putLong(MediaMetadata.METADATA_KEY_DURATION, duration)
                .putString(MediaMetadata.METADATA_KEY_TITLE, title)
                .putString(MediaMetadata.METADATA_KEY_ARTIST, "Rima Lab · Treino de freestyle")
                .putString(MediaMetadata.METADATA_KEY_ALBUM, "Biblioteca de beats")
                .build());
        long actions = PlaybackState.ACTION_PLAY | PlaybackState.ACTION_PAUSE | PlaybackState.ACTION_PLAY_PAUSE
                | PlaybackState.ACTION_SKIP_TO_NEXT | PlaybackState.ACTION_SKIP_TO_PREVIOUS | PlaybackState.ACTION_STOP;
        PlaybackState state = new PlaybackState.Builder()
                .setActions(actions)
                .setState(playing ? PlaybackState.STATE_PLAYING : PlaybackState.STATE_PAUSED,
                        currentPosition, playing ? 1f : 0f, android.os.SystemClock.elapsedRealtime())
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
        currentDuration = in != null ? in.getLongExtra("duration", currentDuration) : currentDuration;
        currentPosition = in != null ? in.getLongExtra("position", currentPosition) : currentPosition;
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


# Alinhamento do botão voltar em todas as seções.
if "</head>" in html and "rima-back-center-v1" not in html:
    html = html.replace("</head>", '<style id="rima-back-center-v1">#lv .bk,#bt .bk{display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;margin-left:auto!important;margin-right:auto!important}</style></head>', 1)

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


# 14) Sincronização definitiva: posição e duração reais no MediaSession, sem remover o player durante troca.
main = main_path.read_text(encoding="utf-8")
main = replace_once(
    main,
    "@JavascriptInterface public void mediaState(int st, String title)",
    "@JavascriptInterface public void mediaState(int st, String title, double duration, double position)",
    "bridge mediaState com duração/posição"
)
main_path.write_text(main, encoding="utf-8")

html = html_path.read_text(encoding="utf-8")
html = replace_once(html,
    "let zMK='';function zMedia(){try{const k=(play?(zPL?1:0):-1)+'|'+(ZS.name||'');if(k==zMK)return;zMK=k;if(window.RimaNative&&RimaNative.mediaState)RimaNative.mediaState(play?(zPL?1:0):-1,ZS.name||'Rima Lab')}catch(e){}}",
    "let zMK='',zMediaAt=0;function zMedia(force){try{const st=play?(zPL?1:0):-1,c=zCur(),d=zDur(),now=performance.now();if(!force&&now-zMediaAt<900)return;zMediaAt=now;const title=ZS.name||'Rima Lab',k=st+'|'+title+'|'+Math.round(d*1000)+'|'+Math.round(c*1000);if(k===zMK)return;zMK=k;if(window.RimaNative&&RimaNative.mediaState)RimaNative.mediaState(st,title,d,c)}catch(e){}}",
    "notificação envia posição e duração"
)
html = replace_once(html,
    "function zSetPL(v){if(v&&!zPL){zPL=1;zW.splice(0).forEach(f=>f())}else if(!v)zPL=0;HOLD=zPL?0:1;if(HOLD){try{speechSynthesis.cancel()}catch(e){}}zBarUI();zMedia()}",
    "function zSetPL(v){if(v&&!zPL){zPL=1;zW.splice(0).forEach(f=>f())}else if(!v)zPL=0;HOLD=zPL?0:1;if(HOLD){try{speechSynthesis.cancel()}catch(e){}}zBarUI();zMedia(true)}",
    "atualização imediata do estado do player"
)
html = replace_once(html,
    "zPL=0;zBarUI()}",
    "zPL=0;zBarUI();if(play)zMedia(true)}",
    "manter notificação viva durante carregamento do próximo beat"
)
html = replace_once(html,
    "function zTick(){zR=requestAnimationFrame(zTick);zUI();if(!play||!zPL||zS||ZS.dp)return;",
    "function zTick(){zR=requestAnimationFrame(zTick);zUI();if(play)zMedia(false);if(!play||!zPL||zS||ZS.dp)return;",
    "atualizar posição da notificação durante reprodução"
)
html = replace_once(html,
    'min="0" max="600" step="1" value="${LAT}"',
    'min="0" max="1200" step="1" value="${LAT}"',
    "slider de calibração até 1200ms"
)
html = replace_once(html,
    "function setLat(v){LAT=v;LATSET=true;",
    "function setLat(v){v=Math.max(0,Math.min(1200,+v||0));LAT=v;LATSET=true;",
    "limite manual de calibração até 1200ms"
)
html = replace_once(html,
    "N=8,W=2,bars=",
    "N=6,W=1,bars=",
    "calibração com sinais separados"
)
html = replace_once(html,
    "T+i*.75",
    "T+i*1.5",
    "intervalo maior entre sinais de calibração"
)
html = replace_once(html,
    "ts[N+W-1]+1,w0=Date.now()",
    "ts[N+W-1]+1.4,w0=Date.now()",
    "janela de captura da calibração"
)
html = replace_once(html,
    "t0+.75-off0",
    "t0+1.25-off0",
    "janela de correlação de até 1250ms"
)
html = replace_once(html,
    "dl<800",
    "dl<1200",
    "aceitar atraso acústico até 1200ms"
)
html = html.replace("Math.min(600,Math.round(fin.ms))","Math.min(1200,Math.round(fin.ms))")
if "</head>" in html and "rima-back-center-v1" not in html:
    html = html.replace("</head>", '<style id="rima-back-center-v1">#lv .bk,#bt .bk{display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;margin-left:auto!important;margin-right:auto!important}</style></head>', 1)
html_path.write_text(html, encoding="utf-8")

print("RUNTIME_PATCH_OK: paisagem, borda pulsante, troca sem salto, filtro de Drill e notificação MediaSession.")



# 16) Relógio interpolado do elemento de áudio: evita degraus de currentTime em WebView Android.
html = html_path.read_text(encoding="utf-8")
clock_old = "const zCur=()=>zA?zA.currentTime:(ZY.ps&&ZY.fz>=0?ZY.fz:(ZY.win.length?zNow()+ZY.o:zL)),zDur=()=>zA?(isFinite(zA.duration)?zA.duration:0):ZY.dur;"
clock_new = """let zClockP=0,zClockT=0,zClockR=1;
const zCur=()=>{if(zA){const p=performance.now()/1000,t=zA.currentTime,r=zA.playbackRate||1;if(!isFinite(t))return 0;if(zA.paused){zClockP=p;zClockT=t;zClockR=r;return t}if(!zClockP||t<zClockT-.12||t>zClockT+.5){zClockP=p;zClockT=t;zClockR=r;return t}const estimate=zClockT+(p-zClockP)*zClockR;if(t>=estimate-.025){zClockP=p;zClockT=t;zClockR=r;return t}return estimate}return ZY.ps&&ZY.fz>=0?ZY.fz:(ZY.win.length?zNow()+ZY.o:zL)},zDur=()=>zA?(isFinite(zA.duration)?zA.duration:0):ZY.dur;"""
if clock_old in html:
    html = html.replace(clock_old, clock_new, 1)
elif clock_new not in html:
    raise SystemExit("CLOCK_PATCH_FAIL: zCur anchor not found")
html = html.replace("function zKill(){zTok++;ZS.loadingAudio=0;", "function zKill(){zTok++;zClockP=0;zClockT=0;ZS.loadingAudio=0;", 1)
html_path.write_text(html, encoding="utf-8")

# 15) Ajuste fino solicitado: botão Voltar à esquerda, texto centralizado, logo R único e calibração de baixa carga.
html = html_path.read_text(encoding="utf-8")
html = html.replace(
    '<style id="rima-back-center-v1">#lv .bk,#bt .bk{display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;margin-left:auto!important;margin-right:auto!important}</style>',
    '<style id="rima-back-center-v2">#lv .bk,#bt .bk{display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;margin-left:0!important;margin-right:auto!important}</style>'
)
if "rima-back-center-v2" not in html and "</head>" in html:
    html = html.replace("</head>", '<style id="rima-back-center-v2">#lv .bk,#bt .bk{display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;margin-left:0!important;margin-right:auto!important}</style></head>', 1)

# O selo do player deve ter somente um R, maior; as barras continuam como equalizador.
html = html.replace('<span>RL</span><i></i><i></i><i></i>', '<span>R</span><i></i><i></i><i></i>')
html = html.replace('#pbar .pw-art span{position:absolute!important;z-index:2!important;top:5px!important;left:5px!important;right:auto!important;bottom:auto!important;display:block!important;line-height:1!important;white-space:nowrap!important;text-shadow:0 1px 3px rgba(0,0,0,.35)!important}',
                    '#pbar .pw-art span{position:absolute!important;z-index:2!important;top:2px!important;left:5px!important;right:auto!important;bottom:auto!important;display:block!important;font-size:24px!important;font-weight:900!important;line-height:1!important;white-space:nowrap!important;text-shadow:0 1px 3px rgba(0,0,0,.35)!important}')
html = html.replace('@media(max-width:370px){#pbar .pw-art span{font-size:11px!important;top:5px!important;left:4px!important}',
                    '@media(max-width:370px){#pbar .pw-art span{font-size:20px!important;top:2px!important;left:4px!important}')

# Calibração acústica: chirp mais curto e banda segura para 4 kHz, captura mais rápida e correlação menos custosa.
html = html.replace(
    'd=Math.max(1,Math.floor(sr/9000)),fs=sr/d,L=Math.round(sr*.22),dur=L/sr,f0=800,f1=3400',
    'd=Math.max(1,Math.ceil(sr/4000)),fs=sr/d,L=Math.round(sr*.12),dur=L/sr,f0=600,f1=1700'
)
html = html.replace('createScriptProcessor(2048,1,1)', 'createScriptProcessor(512,1,1)')
html = html.replace('N=6,W=1,bars=', 'N=7,W=1,bars=')
html = html.replace('T+i*1.5', 'T+i*1.2')
html = html.replace('ts[N+W-1]+1.4,w0=Date.now()', 'ts[N+W-1]+1.3,w0=Date.now()')
html = html.replace('t0+1.25-off0', 't0+1.2-off0')
html = html.replace('if(mx>=.1&&mx>=rr*5)', 'if(mx>=.06&&mx>=rr*4.5)')
# Escolhe o pico de correlação global; não aceita um pico lateral anterior só por ultrapassar 55%.
html = html.replace(
    'let jj=mj;for(let j=lo+1;j<hi-1;j++){const y=va[j-lo];if(y>=.55*mx&&y>=va[j-lo-1]&&y>=va[j-lo+1]){jj=j;break}}let fr=0;',
    'let jj=mj;let fr=0;'
)
html = html.replace(
    'if(ok.length>=4){fin={ms:ok.reduce((u,v)=>u+v,0)/ok.length,n:ok.length};break}',
    'if(ok.length>=5){ok.sort((x,y)=>x-y);fin={ms:ok[Math.floor(ok.length/2)],n:ok.length};break}'
)
html = html.replace('Math.abs(x-md)<=12', 'Math.abs(x-md)<=8')
# A animação do palco termina junto do pulso, sem ficar acesa muito depois da batida.
html = html.replace('setTimeout(()=>e.classList.remove(\'hit\'),145)', 'setTimeout(()=>e.classList.remove(\'hit\'),180)')
html = html.replace('animation:rl-stage-glow .72s ease-out!important', 'animation:rl-stage-glow .18s ease-out!important')
html_path.write_text(html, encoding="utf-8")

print("RUNTIME_PATCH_OK: voltar à esquerda, R único ampliado, calibração acústica otimizada e pulso de palco alinhado.")
