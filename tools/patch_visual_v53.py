#!/usr/bin/env python3
"""Restore normal document scrolling on every non-live Rima Lab screen."""
from pathlib import Path
import re, sys

root = Path(sys.argv[1]).resolve()
html_path = root / "app/src/main/assets/rima-lab.html"
gradle_path = next((p for p in (root/"app/build.gradle", root/"app/build.gradle.kts") if p.exists()), None)
if not html_path.is_file() or gradle_path is None:
    raise SystemExit("V53_FAIL: HTML or Gradle file missing")
html = html_path.read_text(encoding="utf-8")
gradle = gradle_path.read_text(encoding="utf-8")
if "rimalab-global-scroll-system-v53" in html:
    raise SystemExit("V53_FAIL: patch already applied")
if "rimalab-landscape-navigation-touch-runtime-v52" not in html:
    raise SystemExit("V53_FAIL: V52 runtime missing")

# Root cause: V47 uses the generic body.pl flag to lock <main> in landscape.
# trainNext() sets body.pl on setup step 2 too, so setup was mistaken for the
# live stage. Scope that lock to the explicit state created only when #lv opens.
legacy = "body.pl:not(.pv) main,body.pl.sy:not(.pv) main{"
if html.count(legacy) != 1:
    raise SystemExit(f"V53_FAIL: expected one generic V47 main lock, found {html.count(legacy)}")
html = html.replace(legacy, "body.rima-live-landscape main{", 1)

# V52 repaired setup by writing persistent inline !important geometry to main.
# That was a second source of orientation-dependent state. Use classes and CSS
# instead; do not mutate main's position/height/overflow inline.
script_id = "rimalab-landscape-navigation-touch-runtime-v52"
open_tag = f'<script id="{script_id}">'
start = html.find(open_tag)
if start < 0:
    raise SystemExit("V53_FAIL: V52 runtime opening tag missing")
content_start = start + len(open_tag)
end = html.find("</script>", content_start)
if end < 0:
    raise SystemExit("V53_FAIL: V52 runtime closing tag missing")
runtime = r'''(function(){
 'use strict';
 const body=document.body,root=document.documentElement;
 const nav=document.querySelector('body>nav');
 const liveStage=document.getElementById('lv');
 function landscape(){return !!(window.matchMedia&&window.matchMedia('(orientation:landscape)').matches)||innerWidth>innerHeight}
 function sync(){
  const active=landscape()&&!!(liveStage&&!liveStage.hidden)&&body.classList.contains('pl')&&!body.classList.contains('pv');
  body.classList.toggle('rima-live-landscape',active);
  root.classList.toggle('rima-live-landscape',active);
  if(nav&&landscape()&&!active){
   nav.style.setProperty('display','grid','important');
   nav.style.setProperty('visibility','visible','important');
   nav.style.setProperty('pointer-events','auto','important');
  }
 }
 function settle(){requestAnimationFrame(sync);setTimeout(sync,120);setTimeout(sync,320)}
 const observer=new MutationObserver(sync);
 observer.observe(body,{attributes:true,attributeFilter:['class']});
 if(liveStage)observer.observe(liveStage,{attributes:true,attributeFilter:['hidden','class']});
 window.addEventListener('orientationchange',settle,{passive:true});
 window.addEventListener('resize',settle,{passive:true});
 window.addEventListener('pageshow',settle,{passive:true});
 if(window.visualViewport)window.visualViewport.addEventListener('resize',settle,{passive:true});
 settle();
 window.rimaV53SyncScrollState=sync;
})();'''
html = html[:content_start] + runtime + html[end:]

css = r'''<style id="rimalab-global-scroll-system-v53">
/* All normal app screens use document scrolling, independent of orientation.
   The live landscape stage is the only state that locks the page behind it. */
html{
 width:100%!important;max-width:100%!important;height:auto!important;min-height:100%!important;
 overflow-x:hidden!important;overflow-y:auto!important;
 overscroll-behavior-x:none!important;overscroll-behavior-y:auto!important;
 touch-action:pan-y!important;
}
body{
 width:100%!important;max-width:100%!important;height:auto!important;
 min-height:100dvh!important;max-height:none!important;
 overflow-x:hidden!important;overflow-y:visible!important;
 overscroll-behavior-y:auto!important;touch-action:pan-y!important;
}
body:not(.rima-live-landscape) main{
 position:relative!important;inset:auto!important;left:auto!important;right:auto!important;
 top:auto!important;bottom:auto!important;width:100%!important;max-width:100%!important;
 height:auto!important;min-height:100vh!important;max-height:none!important;
 margin:0 auto!important;box-sizing:border-box!important;
 overflow:visible!important;overflow-x:hidden!important;overflow-y:visible!important;
 overscroll-behavior-y:auto!important;touch-action:pan-y!important;
 padding-bottom:calc(104px + env(safe-area-inset-bottom,0px))!important;
}
body:not(.rima-live-landscape) main>.tab:not([hidden]),
body:not(.rima-live-landscape) #su,
body:not(.rima-live-landscape) #bt,
body:not(.rima-live-landscape) #train-step-1,
body:not(.rima-live-landscape) #train-step-2{
 position:relative!important;inset:auto!important;
 height:auto!important;min-height:0!important;max-height:none!important;
 overflow:visible!important;overflow-x:hidden!important;overflow-y:visible!important;
 overscroll-behavior-y:auto!important;touch-action:pan-y!important;
}
body:not(.rima-live-landscape) #train-step-1,
body:not(.rima-live-landscape) #train-step-2{width:100%!important;max-width:100%!important}
body:not(.rima-live-landscape) #bp,
body:not(.rima-live-landscape) #bq{touch-action:pan-y!important}
body.rima-live-landscape,html.rima-live-landscape{
 height:100vh!important;max-height:100vh!important;
 overflow:hidden!important;overscroll-behavior:none!important;
}
body.rima-live-landscape main{
 position:fixed!important;inset:0!important;width:100vw!important;max-width:100vw!important;
 height:100vh!important;max-height:100vh!important;overflow:hidden!important;
 overscroll-behavior:none!important;touch-action:pan-y!important;
}
@media (orientation:landscape) and (min-width:560px){
 body:not(.rima-live-landscape) main{min-height:100vh!important;padding:8px 18px 92px!important}
}
</style>'''
pos = html.lower().rfind("</body>")
if pos < 0:
    raise SystemExit("V53_FAIL: </body> missing")
html = html[:pos] + css + "\n" + html[pos:]

m = re.search(r"\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)", gradle)
if not m or (m.group(1) or m.group(2)) != "73":
    raise SystemExit("V53_FAIL: expected base versionCode 73")
gradle = gradle[:m.start()] + re.sub("73", "74", m.group(0), count=1) + gradle[m.end():]
m = re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]", gradle)
if not m or (m.group(1) or m.group(2)) != "3.3.1":
    raise SystemExit("V53_FAIL: expected base versionName 3.3.1")
gradle = gradle[:m.start()] + m.group(0).replace("3.3.1", "3.3.2") + gradle[m.end():]
html_path.write_text(html, encoding="utf-8")
gradle_path.write_text(gradle, encoding="utf-8")
print("V53_OK: body.pl no longer locks setup screens; main locks only during live landscape; global document scroll works in portrait and landscape; version 3.3.2/code74")
