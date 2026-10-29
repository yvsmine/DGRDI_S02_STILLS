import os, re, shutil, html, json, base64
from urllib.parse import quote
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = "sequences"
serie = html.escape(os.environ.get("SERIE", "Stills"))
PASSWORD = os.environ.get("SITE_PASSWORD", "")
ITER = 200000
exts = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")

def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def folder_key(name):
    return (1 if name.upper().startswith("SANS") else 0, natural(name))

def label(name):
    return html.escape(name.replace("_", " "))

def encrypt(text):
    salt = os.urandom(16)
    iv = os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    key = kdf.derive(PASSWORD.encode())
    ct = AESGCM(key).encrypt(iv, text.encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    return {"s": b(salt), "i": b(iv), "c": b(ct), "n": ITER}

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
#gate{position:fixed;inset:0;display:none;align-items:center;justify-content:center}
#gate form{position:relative;display:inline-block}
#gate input{width:240px;box-sizing:border-box;padding:12px 44px;font-size:16px;text-align:center;
    border-radius:6px;border:1px solid #333;background:#1a1a1a;color:#eee;outline:none}
#gate input:focus{border-color:#666}
#gate input.bad{border-color:#f85149}
#gate button{position:absolute;right:2px;top:0;bottom:0;width:42px;background:none;border:none;
    color:#888;font-size:22px;cursor:pointer}
#gate button:hover{color:#ddd}
"""

LIGHTBOX_HTML = (
    '<div id="lb"><button class="close" aria-label="Fermer">&times;</button>'
    '<button class="prev" aria-label="Précédent">&#8249;</button>'
    '<img id="lb-img" alt="">'
    '<button class="next" aria-label="Suivant">&#8250;</button>'
    '<div class="cap" id="lb-cap"></div></div>'
)

SHELL = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<link rel="icon" href="data:,">
<title>%%TITLE%%</title><style>%%CSS%%</style></head><body>
<div id="gate"><form id="f"><input type="password" id="pw" autocomplete="current-password" aria-label="Mot de passe" enterkeyhint="go"><button type="submit" aria-label="Valider">&rarr;</button></form></div>
<div id="app">%%BODY%%</div>
<script>
var D = %%DATA%%;
var app = document.getElementById('app');
var gate = document.getElementById('gate');
var pw = document.getElementById('pw');

function b64(s){ return Uint8Array.from(atob(s), function(c){ return c.charCodeAt(0); }); }

async function dec(p){
  var enc = new TextEncoder();
  var km = await crypto.subtle.importKey('raw', enc.encode(p), 'PBKDF2', false, ['deriveKey']);
  var key = await crypto.subtle.deriveKey(
    {name:'PBKDF2', salt:b64(D.s), iterations:D.n, hash:'SHA-256'},
    km, {name:'AES-GCM', length:256}, false, ['decrypt']);
  var pt = await crypto.subtle.decrypt({name:'AES-GCM', iv:b64(D.i)}, key, b64(D.c));
  return JSON.parse(new TextDecoder().decode(pt));
}

function initLb(){
  var links = Array.prototype.slice.call(app.querySelectorAll('.grid a'));
  var lb = app.querySelector('#lb');
  if (!links.length || !lb) return;
  var img = lb.querySelector('#lb-img');
  var cap = lb.querySelector('#lb-cap');
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
}

function unlock(o, p){
  try { sessionStorage.setItem('sp', p); } catch(e) {}
  gate.style.display = 'none';
  document.title = o.t;
  app.innerHTML = o.b;
  app.style.display = 'block';
  initLb();
}

async function tryPw(p, silent){
  try {
    unlock(await dec(p), p);
  } catch(e) {
    gate.style.display = 'flex';
    if (!silent) { pw.classList.add('bad'); pw.value = ''; }
    pw.focus();
  }
}

if (!D) {
  initLb();
} else {
  app.style.display = 'none';
  var saved = null;
  try { saved = sessionStorage.getItem('sp'); } catch(e) {}
  if (saved) {
    tryPw(saved, true);
  } else {
    gate.style.display = 'flex';
    pw.focus();
  }
  document.getElementById('f').addEventListener('submit', function(e){
    e.preventDefault();
    pw.classList.remove('bad');
    tryPw(pw.value, false);
  });
}
</script></body></html>"""

def page(title, body):
    if PASSWORD:
        data = json.dumps(encrypt(json.dumps({"t": title, "b": body})))
        inner = ""
        shell_title = "•"
    else:
        data = "null"
        inner = body
        shell_title = title
    return (SHELL.replace("%%TITLE%%", shell_title)
                 .replace("%%CSS%%", CSS)
                 .replace("%%DATA%%", data)
                 .replace("%%BODY%%", inner))

shutil.rmtree("_site", ignore_errors=True)
os.makedirs("_site")

cards = ""
if os.path.isdir(ROOT):
    shutil.copytree(ROOT, f"_site/{ROOT}")
    for folder in sorted(os.listdir(ROOT), key=folder_key):
        d = os.path.join(ROOT, folder)
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
            f'<div class="grid">{thumbs}</div>' + LIGHTBOX_HTML
        )
        with open(f"_site/{ROOT}/{folder}/index.html", "w", encoding="utf-8") as fh:
            fh.write(page(f"{label(folder)} – {serie}", body))

        cards += (
            f'<a class="folder" href="{ROOT}/{quote(folder)}/">'
            f'<img loading="lazy" src="{ROOT}/{quote(folder)}/{quote(files[0])}">'
            f'<div class="info"><span class="name">{label(folder)}</span>'
            f'<span class="count">{len(files)} stills</span></div></a>'
        )

home = f'<h1>{serie}</h1><div class="folders">{cards}</div>'
with open("_site/index.html", "w", encoding="utf-8") as fh:
    fh.write(page(f"{serie} – Stills", home))
