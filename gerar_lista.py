"""Extrai os cursos do HTML exportado (allnet-aws.html), junta os duplicados
(ex.: "X" e "X (Premium)" com os mesmos vídeos) e gera dados/cursos.json e
dados/cursos_por_tamanho.csv ordenados do maior para o menor.

Uso: python gerar_lista.py caminho/allnet-aws.html
Os tamanhos vêm de um HEAD em cada vídeo do S3 (cache em dados/tamanhos.json).
"""
import concurrent.futures as cf
import csv
import json
import os
import re
import sys
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados")


def carregar_html(caminho):
    s = open(caminho, encoding="utf-8").read()
    m = re.search(r'<script id="appdata" type="application/json">(.*?)</script>', s, re.S)
    return json.loads(m.group(1))["courses"]


def aulas_do_curso(c):
    aulas = [(mod["name"], ct) for mod in c["modules"] for ct in mod["contents"]]
    aulas += [("", ct) for ct in c.get("orphanContents") or []]
    return [(m, ct) for m, ct in aulas if ct.get("url")]


def tamanhos(urls):
    cache_path = os.path.join(DADOS, "tamanhos.json")
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    faltam = [u for u in urls if cache.get(u, -1) < 0]

    def head(u):
        for _ in range(3):
            try:
                r = urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=30)
                return u, int(r.headers.get("Content-Length", -1))
            except Exception:
                pass
        return u, -1

    with cf.ThreadPoolExecutor(32) as ex:
        cache.update(dict(ex.map(head, faltam)))
    json.dump(cache, open(cache_path, "w"))
    return cache


def main():
    os.makedirs(DADOS, exist_ok=True)
    cursos = carregar_html(sys.argv[1])
    urls = sorted({ct["url"] for c in cursos for _, ct in aulas_do_curso(c)})
    tam = tamanhos(urls)

    # cursos com exatamente os mesmos vídeos viram um só
    grupos = {}
    for c in cursos:
        aulas = aulas_do_curso(c)
        if aulas:
            grupos.setdefault(frozenset(ct["url"] for _, ct in aulas), []).append((c, aulas))

    saida = []
    for itens in grupos.values():
        nomes = sorted({c["name"] for c, _ in itens})
        principal = min(nomes, key=lambda n: ("inativo" in n.lower(), len(n)))
        videos, vistos = [], set()
        for mod, ct in itens[0][1]:
            if ct["url"] in vistos:
                continue
            vistos.add(ct["url"])
            videos.append({"modulo": mod, "nome": ct["name"], "url": ct["url"],
                           "bytes": max(tam.get(ct["url"], 0), 0),
                           "vimeo_aws": bool(ct.get("isVimeoAws"))})
        saida.append({"curso": principal, "nomes": nomes, "aulas": len(videos),
                      "bytes": sum(v["bytes"] for v in videos),
                      "aulas_vimeo_aws": sum(v["vimeo_aws"] for v in videos),
                      "videos": videos})

    saida.sort(key=lambda x: -x["bytes"])
    for i, c in enumerate(saida, 1):
        c["rank"] = i
    json.dump(saida, open(os.path.join(DADOS, "cursos.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(DADOS, "cursos_por_tamanho.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["rank", "curso", "GB", "aulas", "aulas_origem_vimeo", "outros_nomes"])
        for c in saida:
            w.writerow([c["rank"], c["curso"], f'{c["bytes"] / 1e9:.2f}'.replace(".", ","),
                        c["aulas"], c["aulas_vimeo_aws"],
                        " | ".join(n for n in c["nomes"] if n != c["curso"])])
    print(f"{len(cursos)} cursos no HTML -> {len(saida)} cursos únicos, "
          f"{sum(c['bytes'] for c in saida) / 1e9:.1f} GB")


if __name__ == "__main__":
    main()
