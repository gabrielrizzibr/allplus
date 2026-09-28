"""Checklist curso a curso: HTML (todos os cursos) -> Vimeo (etapa antes) -> Site (destino).

Uso: python comparar.py vimeo.txt site.txt

vimeo.txt: de preferência "pasta<TAB>vídeo" por linha (pasta = curso no Vimeo),
           mas aceita só o título do vídeo/pasta por linha.
site.txt:  um curso por linha (se tiver aulas, "curso<TAB>aula").

Gera em dados/:
  - checklist.csv / checklist.md   todos os cursos, do maior pro menor:
        curso | GB | Vimeo ✅/⚠️ x/y/❌ | Site ✅/❌ | próximo passo | aulas faltando no Vimeo
  - falta_no_site.txt              completo no Vimeo, falta no site
  - vimeo_incompleto.txt           no Vimeo, mas faltando aulas
  - nao_esta_em_lugar_nenhum.txt   só no HTML -> baixar e subir no Vimeo
"""
import csv
import difflib
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados")
IGNORAR = {"teste"}  # vídeos de teste no HTML que não precisam subir


def normalizar(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\((premium)\)|-\s*inativo|\.(mp4|mov|mkv)$", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    romanos = {"i": "1", "ii": "2", "iii": "3", "iv": "4"}
    return " ".join(romanos.get(p, p) for p in s.split())


def carregar(caminho):
    """Retorna {pasta_normalizada: {titulos}} e o conjunto de todos os títulos."""
    pastas, todos = {}, set()
    if not caminho or not os.path.exists(caminho):
        return pastas, todos
    with open(caminho, encoding="utf-8", errors="ignore") as f:
        for linha in f:
            partes = [normalizar(p) for p in linha.rstrip("\n").split("\t")]
            partes = [p for p in partes if p]
            if not partes:
                continue
            todos.update(partes)
            if len(partes) >= 2:
                pastas.setdefault(partes[0], set()).add(partes[-1])
    return pastas, todos


def bate(nome, titulos):
    n = normalizar(nome)
    if not n:
        return False
    if n in titulos:
        return True
    # um contém o outro, mas só com palavras inteiras ("modulo 1" não bate com "modulo 12")
    contem = lambda a, b: re.search(rf"(^| ){re.escape(a)}( |$)", b)
    if len(n) >= 12 and any(contem(n, t) or (len(t) >= 12 and contem(t, n)) for t in titulos):
        return True
    # nome parecido (erro de digitação), mas os números têm que ser iguais
    numeros = re.findall(r"\d+", n)
    return any(re.findall(r"\d+", t) == numeros
               for t in difflib.get_close_matches(n, titulos, n=3, cutoff=0.9))


def situacao(curso, pastas, todos):
    """(curso_encontrado, aulas_encontradas, aulas_faltando)."""
    aulas = [v["nome"] for v in curso["videos"] if normalizar(v["nome"]) not in IGNORAR]
    # 1) existe uma pasta com o nome do curso? compara as aulas dentro dela
    pasta = next((p for p in pastas for n in curso["nomes"] if bate(n, {p})), None)
    if pasta:
        faltam = [a for a in aulas if not bate(a, pastas[pasta])]
        # curso de aula única costuma ter o vídeo com o próprio nome do curso
        if len(aulas) == 1 and faltam and bate(curso["curso"], pastas[pasta]):
            faltam = []
        return True, len(aulas) - len(faltam), faltam
    # 2) sem pasta: o título do curso aparece solto, ou a maioria das aulas aparece
    achou_nome = any(bate(n, todos) for n in curso["nomes"])
    faltam = [a for a in aulas if not bate(a, todos)]
    if len(aulas) == 1 and achou_nome:
        faltam = []
    achou = achou_nome or (aulas and (len(aulas) - len(faltam)) / len(aulas) >= 0.5)
    return bool(achou), len(aulas) - len(faltam), faltam


def main():
    vp, vt = carregar(sys.argv[1] if len(sys.argv) > 1 else None)
    sp, st = carregar(sys.argv[2] if len(sys.argv) > 2 else None)
    cursos = json.load(open(os.path.join(DADOS, "cursos.json"), encoding="utf-8"))

    linhas, falta_site, incompleto, nenhum = [], [], [], []
    for c in cursos:
        total = sum(normalizar(v["nome"]) not in IGNORAR for v in c["videos"])
        no_vimeo, achadas, faltam = situacao(c, vp, vt)
        no_site = situacao(c, sp, st)[0]

        if not no_vimeo:
            vimeo = "❌"
        elif faltam:
            vimeo = f"⚠️ {achadas}/{total}"
        else:
            vimeo = f"✅ {total}/{total}"
        site = "✅" if no_site else "❌"

        if no_site:
            passo = "ok"
        elif no_vimeo and not faltam:
            passo, _ = "subir no site", falta_site.append(c)
        elif no_vimeo:
            passo, _ = f"completar Vimeo (faltam {len(faltam)}) e subir no site", incompleto.append((c, faltam))
        else:
            passo, _ = "baixar e subir no Vimeo", nenhum.append(c)
        linhas.append((c, vimeo, site, passo, faltam if no_vimeo else []))

    with open(os.path.join(DADOS, "checklist.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["rank", "curso", "GB", "aulas", "vimeo", "site", "proximo_passo", "aulas_faltando_no_vimeo"])
        for c, vimeo, site, passo, faltam in linhas:
            w.writerow([c["rank"], c["curso"], f'{c["bytes"] / 1e9:.2f}'.replace(".", ","), c["aulas"],
                        vimeo, site, passo, " | ".join(faltam)])

    with open(os.path.join(DADOS, "checklist.md"), "w", encoding="utf-8") as f:
        f.write("| # | Curso | GB | Vimeo | Site | Próximo passo |\n|---|---|---|---|---|---|\n")
        for c, vimeo, site, passo, _ in linhas:
            f.write(f'| {c["rank"]} | {c["curso"]} | {c["bytes"] / 1e9:.2f} | {vimeo} | {site} | {passo} |\n')

    def salvar(nome, lista):
        with open(os.path.join(DADOS, nome), "w", encoding="utf-8") as f:
            for item in lista:
                c, faltam = item if isinstance(item, tuple) else (item, [])
                f.write(f'{c["rank"]}\t{c["bytes"] / 1e9:.2f} GB\t{c["curso"]}\n')
                for a in faltam:
                    f.write(f"\t\t  falta: {a}\n")

    salvar("falta_no_site.txt", falta_site)
    salvar("vimeo_incompleto.txt", incompleto)
    salvar("nao_esta_em_lugar_nenhum.txt", nenhum)

    ok = sum(p == "ok" for _, _, _, p, _ in linhas)
    print(f"{len(cursos)} cursos | no site: {ok} | Vimeo completo, falta site: {len(falta_site)} | "
          f"Vimeo incompleto: {len(incompleto)} | em lugar nenhum: {len(nenhum)} "
          f"({sum(c['bytes'] for c in nenhum) / 1e9:.1f} GB)")
    for c, vimeo, site, passo, _ in linhas[:25]:
        print(f'  #{c["rank"]:<4} {c["bytes"] / 1e9:6.2f} GB  Vimeo {vimeo:<9} Site {site}  {passo:<45} {c["curso"]}')


if __name__ == "__main__":
    main()
