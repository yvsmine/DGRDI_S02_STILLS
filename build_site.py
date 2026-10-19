import os, re, shutil, html

serie = html.escape(os.environ.get("SERIE", "Stills"))
exts = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")

def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

shutil.rmtree("_site", ignore_errors=True)
os.makedirs("_site")
if os.path.isdir("episodes"):
    shutil.copytree("episodes", "_site/episodes")

sections = ""
if os.path.isdir("episodes"):
    for ep in sorted(os.listdir("episodes"), key=natural):
        files = sorted(
            [f for f in os.listdir(f"episodes/{ep}") if f.lower().endswith(exts)],
            key=natural,
        )
        if not files:
            continue
        cards = "".join(
            f'<a href="episodes/{ep}/{f}" target="_blank">'
            f'<img loading="lazy" src="episodes/{ep}/{f}"><span>{html.escape(f)}</span></a>'
            for f in files
        )
        sections += (
            f'<h2 id="{ep}">{ep.replace("_", " ")} '
            f'<small>({len(files)} stills)</small></h2><div class="grid">{cards}</div>'
        )

page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
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
