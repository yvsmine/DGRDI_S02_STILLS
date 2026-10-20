import os, re, shutil, html
from urllib.parse import quote

serie = html.escape(os.environ.get("SERIE", "Stills"))
exts = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")
prefix = re.compile(r"^ep_([0-9]+(?:\s*-\s*[0-9]+)*)_", re.I)

def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def episodes_of(name):
    m = prefix.match(name)
    if not m:
        return []
    return sorted(set(int(n) for n in re.findall(r"\d+", m.group(1))))

shutil.rmtree("_site", ignore_errors=True)
os.makedirs("_site")

by_ep = {}
if os.path.isdir("episodes"):
    shutil.copytree("episodes", "_site/episodes")
    for folder in os.listdir("episodes"):
        d = os.path.join("episodes", folder)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.lower().endswith(exts):
                for ep in episodes_of(f):
                    by_ep.setdefault(ep, []).append((f, f"episodes/{folder}/{f}"))

sections = ""
for ep in sorted(by_ep):
    items = sorted(by_ep[ep], key=lambda x: natural(x[0]))
    cards = "".join(
        f'<a href="{quote(p)}" target="_blank">'
        f'<img loading="lazy" src="{quote(p)}"><span>{html.escape(f)}</span></a>'
        for f, p in items
    )
    sections += (
        f'<h2 id="EP_{ep}">EP {ep} '
        f'<small>({len(items)} stills)</small></h2><div class="grid">{cards}</div>'
    )

page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{serie} – Stills</title>
<style>
body{{font-family:system-ui,sans-serif;background:#111;color:#eee;margin:0;padding:24px}}
h1{{margin:0 0 24px}} h2{{margin:32px 0 12px;border-bottom:1px solid #333;padding-bottom:6px}}
small{{color:#888;font-weight:normal}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
.grid a{{color:#aaa;text-decoration:none;font-size:12px}}
.grid img{{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:4px;display:block}}
</style></head><body><h1>{serie}</h1>{sections}</body></html>"""

open("_site/index.html", "w", encoding="utf-8").write(page)
