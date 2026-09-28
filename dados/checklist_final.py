"""Junta etapa 2 (dados/etapa2_vimeo.csv) e etapa 3 (dados/site_allplus.tsv) no checklist final."""
import csv
import json
import os

D = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(D, "cursos.json"), encoding="utf-8"))
site = {int(r["rank_html"]): int(r["aulas"])
        for r in csv.DictReader(open(os.path.join(D, "site_allplus.tsv"), encoding="utf-8"), delimiter="\t")
        if r["rank_html"]}
vim = {int(r["rank"]): r["vimeo"]
       for r in csv.DictReader(open(os.path.join(D, "etapa2_vimeo.csv"), encoding="utf-8-sig"), delimiter=";")}

rows = []
for c in C:
    r, v, s = c["rank"], vim[c["rank"]], site.get(c["rank"])
    # tolerância de 1 aula (ex.: introdução juntada com a 1ª aula)
    st = "❌" if s is None else ("✅" if s >= c["aulas"] - 1 else f"⚠️ {s}/{c['aulas']} aulas")
    # prioridade é o site; o Vimeo é o backup/etapa do fluxo (baixar → Vimeo → site)
    if st == "✅":
        p = "ok" if v.startswith("✅") else "ok no site (Vimeo incompleto: completar depois)"
    elif s is not None and v.startswith("✅"):
        p = "completar aulas no site (já estão no Vimeo)"
    elif s is not None:
        p = "completar aulas: baixar → Vimeo → site"
    elif v.startswith("✅"):
        p = "subir no site (já está no Vimeo)"
    elif v.startswith("❌"):
        p = "baixar → Vimeo → site"
    else:
        p = "refazer/completar Vimeo → site"
    rows.append([r, c["curso"], f"{c['segundos'] / 3600:.1f}".replace(".", ","), c["aulas"], c["modulos"], v, st, p])

with open(os.path.join(D, "checklist_final.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["rank", "curso", "horas", "aulas", "modulos", "vimeo", "site", "proximo_passo"])
    w.writerows(rows)
with open(os.path.join(D, "nao_esta_em_lugar_nenhum.txt"), "w", encoding="utf-8") as f:
    for x in rows:
        if x[7] == "baixar → Vimeo → site":
            f.write(f"{x[0]}\t{x[2]} h\t{x[3]} aulas\t{x[1]}\n")
for x in rows:
    if x[5][0] != "❌" or x[6] != "❌":
        print(x)
