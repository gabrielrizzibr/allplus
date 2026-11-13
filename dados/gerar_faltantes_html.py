"""Gera dados/faltantes_site.html: cursos do HTML que faltam (ou estão incompletos) no site."""
import csv, json, html, pathlib
base = pathlib.Path(__file__).parent
cursos = {c['rank']: c for c in json.load(open(base/'cursos.json', encoding='utf-8'))}
rows = list(csv.DictReader(open(base/'checklist_final.csv', encoding='utf-8-sig'), delimiter=';'))

def hm(s):
    s = int(round(s)); return f"{s//3600}h{(s%3600)//60:02d}"

falt, inc = [], []
for r in rows:
    if r['site'].startswith('✅'): continue
    c = cursos[int(r['rank'])]
    (inc if r['site'].startswith('⚠') else falt).append((r, c))

def bloco(r, c, extra=''):
    mods = {}
    for v in c['videos']:
        mods.setdefault(v.get('modulo') or '', []).append(v)
    det = []
    for m, vs in mods.items():
        if m: det.append(f"<div class=mod>{html.escape(m)} <span>{hm(sum(v.get('segundos') or 0 for v in vs))}</span></div>")
        det += [f"<div class=aula>{html.escape(v['nome'])} <span>{hm(v.get('segundos') or 0)}</span></div>" for v in vs]
    nome = html.escape(c['curso'])
    return (f"<details data-n=\"{nome.lower()}\"><summary><b>{r['rank']}</b><i>{nome}</i>"
            f"<em>{hm(c['segundos'])}</em><em>{c['aulas']} aulas</em><em>{c['modulos'] or '–'} mód.</em>{extra}</summary>"
            f"<div class=det>{''.join(det)}</div></details>")

tf = sum(c['segundos'] for _, c in falt); ti = sum(c['segundos'] for _, c in inc)
af = sum(c['aulas'] for _, c in falt)
out = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Cursos faltantes no site</title><style>
:root{{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#e3e3e3;--acc:#0b7a75;--warn:#b26a00}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111;--fg:#eee;--mut:#999;--line:#2a2a2a;--acc:#3cc9c0;--warn:#f0a43a}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;max-width:980px;padding:16px}}
h1{{font-size:22px;margin:4px 0}}h2{{font-size:17px;margin:28px 0 6px}}
.kpi{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}}.kpi div{{border:1px solid var(--line);border-radius:8px;padding:8px 12px}}
.kpi b{{display:block;font-size:20px;color:var(--acc)}}.kpi small{{color:var(--mut)}}
input{{width:100%;box-sizing:border-box;padding:9px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font-size:15px}}
details{{border-bottom:1px solid var(--line)}}summary{{display:flex;gap:10px;padding:7px 2px;cursor:pointer;align-items:baseline}}
summary b{{color:var(--mut);font-weight:400;min-width:30px;font-variant-numeric:tabular-nums}}summary i{{font-style:normal;flex:1}}
summary em{{font-style:normal;color:var(--mut);font-variant-numeric:tabular-nums;white-space:nowrap;min-width:58px;text-align:right}}
summary strong{{color:var(--warn);font-weight:600;white-space:nowrap}}
.det{{padding:2px 0 10px 40px;font-size:13.5px}}.mod{{font-weight:600;margin-top:6px}}.aula{{color:var(--mut);padding-left:12px}}
.det span{{float:right;font-variant-numeric:tabular-nums}}p.nota{{color:var(--mut);font-size:13px}}
@media (max-width:600px){{summary{{flex-wrap:wrap}}summary i{{flex-basis:80%}}.det{{padding-left:8px}}}}
</style></head><body>
<h1>Cursos do HTML que faltam no site allplusead.com.br</h1>
<p class=nota>Base: backup allnet (HTML, 486 cursos únicos) × site conferido por prints em 13/11/2026 (23 cursos). Ordem = maior carga horária primeiro. Clique num curso para ver módulos e aulas com duração.</p>
<div class=kpi><div><b>{len(falt)}</b><small>cursos não estão no site</small></div>
<div><b>{hm(tf)}</b><small>horas desses cursos</small></div><div><b>{af}</b><small>aulas</small></div>
<div><b>{len(inc)}</b><small>incompletos no site ({hm(ti)} no total)</small></div></div>
<input id=q placeholder="Buscar curso…" oninput="for(const d of document.querySelectorAll('details'))d.hidden=!d.dataset.n.includes(this.value.toLowerCase())">
<h2>Incompletos no site — completar as aulas</h2>
{''.join(bloco(r,c,f"<strong>site: {html.escape(r['site'].replace('⚠️','').strip())}</strong>") for r,c in inc)}
<h2>Não estão no site — {len(falt)} cursos, {hm(tf)}</h2>
{''.join(bloco(r,c) for r,c in falt)}
</body></html>"""
(base/'faltantes_site.html').write_text(out, encoding='utf-8')
print(len(falt), hm(tf), af, len(inc), hm(ti))
