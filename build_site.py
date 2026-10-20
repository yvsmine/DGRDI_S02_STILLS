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
.grid a{font-size:12px}
.grid img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:4px;display:block}
"""

def page(title, body):
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"
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
            f'<a href="{quote(f)}" target="_blank">'
            f'<img loading="lazy" src="{quote(f)}"><span>{html.escape(f)}</span></a>'
            for f in files
        )
        body = (
            '<a class="back" href="../../">&larr; Retour aux dossiers</a>'
            f'<h1>{label(folder)} <small>({len(files)} stills)</small></h1>'
            f'<div class="grid">{thumbs}</div>'
        )
        with open(f"_site/episodes/{folder}/index.html", "w", encoding="utf-8") as fh:
            fh.write(page(f"{label(folder)} – {serie}", body))

        cards += (
            f'<a class="folder" href="episodes/{quote(folder)}/">'
            f'<img loading="lazy" src="episodes/{quote(folder)}/{quote(files[0])}">'
            f'<div class="info"><span class="name">{label(folder)}</span>'
            f'<span class="count">{len(files)} stills</span></div></a>'
        )

home = f'<h1>{serie}</h1><div class="folders">{cards}</div>'
with open("_site/index.html", "w", encoding="utf-8") as fh:
    fh.write(page(f"{serie} – Stills", home))
