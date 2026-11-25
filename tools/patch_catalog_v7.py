from pathlib import Path
import re,sys
r=Path(sys.argv[1]); p=r/'app/src/main/assets/rima-lab.html'; h=p.read_text()
def rep(a,b,n):
 global h
 if a not in h:
  if b in h:return
  raise SystemExit('PATCH_V7_FAIL '+n)
 h=h.replace(a,b,1)
rep("const ZCACHE_MS=12*60*60*1000;","const ZCACHE_MS=12*60*60*1000;\nconst RIMA_CATALOG_CAP_VERSION='rimalab-70-each-v7';try{if(localStorage.getItem('rima_catalog_cap_version')!==RIMA_CATALOG_CAP_VERSION){['jmraw8','jmraw7','jmraw6'].forEach(k=>localStorage.removeItem(k));['Boom bap','Trap','Drill'].forEach(st=>localStorage.removeItem('jmraw8_at_'+st));localStorage.setItem('rima_catalog_cap_version',RIMA_CATALOG_CAP_VERSION)}}catch(e){}","cache")
rep("function zCacheFresh(st){try{const rows=Array.isArray(ZRAW[st])?ZRAW[st].length:0;return rows>=1&&Date.now()-(+localStorage.getItem('jmraw8_at_'+st)||0)<ZCACHE_MS}catch(e){return false}}","function zCacheFresh(st){try{const rows=Array.isArray(ZRAW[st])?ZRAW[st].length:0;return rows>=70&&Date.now()-(+localStorage.getItem('jmraw8_at_'+st)||0)<ZCACHE_MS}catch(e){return false}}","fresh")
rep("function zBuild(st){const L=(ZRAW[st]||[]).slice(),seen=new Set(L.map(x=>String(x[4])));","function zBuild(st){const L=(ZRAW[st]||[]).slice(0,70),seen=new Set(L.map(x=>String(x[4])));","build")
rep("ZRAW[st]=merged;if(incoming.length||ok){zSv('jmraw8',ZRAW);","ZRAW[st]=merged.slice(0,70);if(incoming.length||ok){zSv('jmraw8',ZRAW);","cachecap")
rep("['search','drill battle beat'],['search','uk drill rap instrumental'],['search','dark drill type beat']","['search','drill battle beat'],['search','uk drill rap instrumental'],['search','dark drill type beat'],['search','ny drill beat instrumental no vocals'],['search','uk drill freestyle beat no vocals'],['search','brazilian drill beat no vocals'],['search','drill cypher instrumental'],['search','dark uk drill instrumental beat'],['search','orchestral drill instrumental'],['search','piano drill beat instrumental'],['search','808 drill instrumental no vocals'],['search','drill type beat instrumental 140 bpm'],['search','hard drill rap instrumental'],['search','street drill beat instrumental'],['search','freestyle battle drill beat'],['search','uk drill instrumental no vocals']","drill queries")
rep("function zLS(s){ZS.s=s;if(ZJS[s]!='load'&&(!Array.isArray(ZRAW[s])||!zCacheFresh(s)))zJm(s);pk()}","function zLS(s){ZS.s=s;if(ZJS[s]!='load'&&(!Array.isArray(ZRAW[s])||!zCacheFresh(s)))zJm(s);pk()}\nfunction zCatLoading(s){return ZJS[s]==='load'||ZJS[s]==='cached'||(ZLIB[s][1].length<70&&!['err','off','nokey','empty'].includes(ZJS[s]))}","loading")
rep("${s} <small>${ZLIB[s][1].length} faixas</small>","${s} <small>${ZLIB[s][1].length}/70</small>${zCatLoading(s)?'<span class=\"rima-cat-spinner\" aria-label=\"Carregando\"></span>':''}","spinner")
rep("Escolha uma base para ouvir e treinar. Toque na seta para salvar no celular.","Ouça o beat até o fim uma vez. Se a licença permitir, ele será salvo automaticamente para ouvir offline.","copy")
rep("function zEnd(my){if(my!=zTok)return;const L=ZLIB[ZS.s][1];","function zEnd(my){if(my!=zTok)return;const L=ZLIB[ZS.s][1];if(ZS.k==='lib'&&ZS.key){const x=L.find(y=>zKey(y)===ZS.key),once='rima_auto_saved_'+ZS.key;try{if(x&&x[10]===true&&x[9]&&!zIsLocal(x)&&localStorage.getItem(once)!=='1'){localStorage.setItem(once,'1');const ix=L.indexOf(x);if(ix>=0)zDl(ix)}}catch(e){}}","auto-save")
rep("function lvStart(){ZNR=1;if(ZS.k!='syn'&&!ZS.key){zFlash('Escolha um beat da lista (Boom bap, Trap ou Drill).');try{$('#bp').scrollIntoView({behavior:'smooth'})}catch(e){}return}","function lvStart(){ZNR=1;if(ZS.k!='syn'&&!ZS.key){try{go(0);if($('#train-step-2'))$('#train-step-2').hidden=true;if($('#train-step-1'))$('#train-step-1').hidden=false;const bp=$('#bp');if(bp){bp.classList.remove('rima-select-focus');void bp.offsetWidth;bp.classList.add('rima-select-focus');setTimeout(()=>bp.scrollIntoView({behavior:'smooth',block:'center'}),80);setTimeout(()=>bp.classList.remove('rima-select-focus'),1800)}}catch(e){}zFlash('Escolha um beat para começar o treino.');return}","missing beat")
const css='<style id="rima-catalog-v7">.rima-cat-spinner{display:inline-block;width:11px;height:11px;margin-left:6px;vertical-align:-1px;border:2px solid rgba(215,251,87,.22);border-top-color:#d7fb57;border-radius:50%;animation:rima-cat-spin .72s linear infinite}@keyframes rima-cat-spin{to{transform:rotate(360deg)}}#bp.rima-select-focus{animation:rima-select-focus 1.4s ease-in-out 2}@keyframes rima-select-focus{50%{filter:drop-shadow(0 0 9px rgba(215,251,87,.7))}}</style>';
if(!h.includes('id="rima-catalog-v7"'))h=h.replace('</head>',css+'</head>');
p.write_text(h)
const icon=r/'app/src/main/res/drawable/ic_stat_beat.xml';
icon.write_text('<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="#FFFFFF" android:pathData="M4,2.5h9.2c4.6,0 7.3,2.4 7.3,6.4 0,2.8 -1.4,4.8 -3.9,5.7L21,21.5h-5.2l-4.1,-6.9H8.4v6.9H4V2.5zM8.4,6.5v4.1h4.5c2,0 3,-.7 3,-2.1s-1,-2-3,-2H8.4z"/></vector>');
const sp=r/'app/src/main/java/app/rimalab/MusicService.java';let s=sp.read_text();
s=s.replace('.setLargeIcon(art())','.setLargeIcon(appLogo())',1);
if(!s.includes('private Bitmap appLogo()')){const i=s.indexOf('    /** Capa do beat:');s=s.slice(0,i)+`    /** Identidade visual oficial do Rima Lab na notificação. */
    private Bitmap appLogo() {
        int size=256; Bitmap b=Bitmap.createBitmap(size,size,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(b); Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setColor(0xFF18200F); c.drawRoundRect(new RectF(0,0,size,size),58,58,p);
        android.graphics.drawable.Drawable mark=getDrawable(R.drawable.ic_fg);
        if(mark!=null){int inset=28;mark.setBounds(inset,inset,size-inset,size-inset);mark.draw(c);}
        return b;
    }
}
`}
sp.write_text(s);
const gp=r/'app/build.gradle';let g=gp.read_text();g=g.replace(/versionCode\s+\d+/, 'versionCode 24');g=g.replace(/versionName\s+['"][^'"]+['"]/, "versionName '2.8.7'");gp.write_text(g);
print('CATALOG_V7_OK');
