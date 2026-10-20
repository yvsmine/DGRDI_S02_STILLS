import os, re, shutil, html
from urllib.parse import quote

serie = html.escape(os.environ.get("SERIE", "Stills"))
exts = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")

def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def folder_key(name):
    return (0 if name.upper().startswith("EP_") else 1, natural(name))

def label(name):
    return html.escape(name.replace("_", " "))

CSS = """
body{font-family:system-ui,sans-serif;background:#111;color:#eee;margin:0;padding:24px}
h1{margin:0 0 24px}
a{color:#aaa;text-decoration:none}
.back{display:inline-block;margin-bottom:16px;color:#ccc;font-size:14px}
.back:hover{color:#fff}
small{color:#888;font-weight:normal}
.folders{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}
.folder{background:#1a1a1a;border-radius:8px;overflow:hidden;display:block;color:#eee}
.folder:hover{background:#242424}
.folder img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}
.folder .info{padding:10px 12px}
.folder .name{font-weight:600;font-size:16px;display:block}
.folder .count{color:#888;font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.grid a{font-size:12px;cursor:zoom-in}
.grid img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:4px;display:block}
#lb{display:none;position:fixed;inset:0;background:rgba(0,0,0,.95);z-index:100;
    align-items:center;justify-content:center;flex-direction:column;touch-action:pan-y}
#lb.open{display:flex}
#lb img{max-width:96vw;max-height:84vh;object-fit:contain;user-select:none}
#lb .cap{color:#ccc;font-size:13px;margin-top:12px;text-align:center;padding:0 16px}
#lb button{position:absolute;background:none;border:none;color:#fff;cursor:pointer;
    font-size:44px;line-height:1;padding:16px;opacity:.7}
#lb button:hover{opacity:1}
#lb .prev{left:4px;top:50%;transform:translateY(-50%)}
#lb .next{right:4px;top:50%;transform:translateY(-50%)}
#lb .close{right:8px;top:4px;font-size:36px}
"""

LIGHTBOX_HTML = (
    '<div id="lb"><button class="close" aria-label="Fermer">&times;</button>'
    '<button class="prev" aria-label="Précédent">&#8249;</button>'
    '<img id="lb-img" alt="">'
    '<button class="next" aria-label="Suivant">&#8250;</button>'
    '<div class="cap" id="lb-cap"></div></div>'
)

LIGHTBOX_JS = """
<script>
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.grid a'));
  var lb = document.getElementById('lb');
  var img = document.getElementById('lb-img');
  var cap = document.getElementById('lb-cap');
  var cur = 0;
  function show(i){
    cur = (i + links.length) % links.length;
    img.src = links[cur].getAttribute('href');
    cap.textContent = links[cur].getAttribute('data-name') + '  —  ' + (cur + 1) + ' / ' + links.length;
    var n = new Image(); n.src = links[(cur + 1) % links.length].getAttribute('href');
    var p = new Image(); p.src = links[(cur - 1 + links.length) % links.length].getAttribute('href');
  }
  function open(i){ show(i); lb.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function close(){ lb.classList.remove('open'); document.body.style.overflow = ''; img.src = ''; }
  links.forEach(function(a, i){
    a.addEventListener('click', function(e){ e.preventDefault(); open(i); });
  });
  lb.querySelector('.close').addEventListener('click', close);
  lb.querySelector('.prev').addEventListener('click', function(e){ e.stopPropagation(); show(cur - 1); });
  lb.querySelector('.next').addEventListener('click', function(e){ e.stopPropagation(); show(cur + 1); });
  lb.addEventListener('click', function(e){ if (e.target === lb) close(); });
  document.addEventListener('keydown', function(e){
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(cur - 1);
    else if (e.key === 'ArrowRight') show(cur + 1);
  });
  var x0 = null;
  lb.addEventListener('touchstart', function(e){ x0 = e.touches[0].clientX; }, {passive:true});
  lb.addEventListener('touchend', function(e){
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(dx < 0 ? cur + 1 : cur - 1);
    x0 = null;
  });
})();
</script>
"""

def page(title, body, extra=""):
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}{extra}</body></html>"
    )

shutil.rmtree("_site", ignore_errors=True)
os.makedirs("_site")

cards = ""
if os.path.isdir("episodes"):
    shutil.copytree("episodes", "_site/episodes")
    for folder in sorted(os.listdir("episodes"), key=folder_key):
        d = os.path.join("episodes", folder)
        if not os.path.isdir(d):
            continue
        files = sorted(
            [f for f in os.listdir(d) if f.lower().endswith(exts)], key=natural
        )
        if not files:
            continue

        thumbs = "".join(
            f'<a href="{quote(f)}" data-name="{html.escape(f, quote=True)}">'
            f'<img loading="lazy" src="{quote(f)}"><span>{html.escape(f)}</span></a>'
            for f in files
        )
        body = (
            '<a class="back" href="../../">&larr; Retour aux dossiers</a>'
            f'<h1>{label(folder)} <small>({len(files)} stills)</small></h1>'
            f'<div class="grid">{thumbs}</div>'
        )
        with open(f"_site/episodes/{folder}/index.html", "w", encoding="utf-8") as fh:
            fh.write(
                page(f"{label(folder)} – {serie}", body, LIGHTBOX_HTML + LIGHTBOX_JS)
            )

        cards += (
            f'<a class="folder" href="episodes/{quote(folder)}/">'
            f'<img loading="lazy" src="episodes/{quote(folder)}/{quote(files[0])}">'
            f'<div class="info"><span class="name">{label(folder)}</span>'
            f'<span class="count">{len(files)} stills</span></div></a>'
        )

home = f'<h1>{serie}</h1><div class="folders">{cards}</div>'
with open("_site/index.html", "w", encoding="utf-8") as fh:
    fh.write(page(f"{serie} – Stills", home))
